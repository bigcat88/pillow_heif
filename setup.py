#!/usr/bin/env python
"""Script to build wheel."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from re import finditer
from shutil import copy
from warnings import warn

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

# pylint: disable=too-many-branches disable=too-many-statements disable=too-many-locals
LIBHEIF_ROOT = None
PLATFORM_MINGW = os.name == "nt" and "GCC" in sys.version


class RequiredDependencyException(Exception):
    """Raised when no ``libheif`` is found."""


def get_version() -> str:
    """Returns version of the project."""
    match = re.search(r'__version__\s*=\s*"(.*?)"', Path("pillow_heif/_version.py").read_text(encoding="utf-8"))
    return match.group(1)


def _cmd_exists(cmd: str) -> bool:
    """Checks if specified command exists on the machine."""
    if "PATH" not in os.environ:
        return False
    return any(os.access(os.path.join(path, cmd), os.X_OK) for path in os.environ["PATH"].split(os.pathsep))


def _pkg_config(name: str) -> tuple[list[str], list[str]] | None:
    command = os.environ.get("PKG_CONFIG", "pkg-config")
    for keep_system in (True, False):
        try:
            command_libs = [command, "--libs-only-L", name]
            command_cflags = [command, "--cflags-only-I", name]
            stderr = None
            if keep_system:
                command_libs.append("--keep-system-libs")
                command_cflags.append("--keep-system-cflags")
                stderr = subprocess.DEVNULL
            libs = re.split(
                r"(^|\s+)-L",
                subprocess.check_output(command_libs, stderr=stderr).decode("utf8").strip(),
            )[
                ::2
            ][1:]
            cflags = re.split(
                r"(^|\s+)-I",
                subprocess.check_output(command_cflags).decode("utf8").strip(),
            )[
                ::2
            ][1:]
            return libs, cflags
        except Exception:  # noqa  # pylint: disable=broad-exception-caught
            pass
    return None


class PillowHeifBuildExt(build_ext):
    """Class based on the Pillow setup method."""

    def build_extensions(self) -> None:  # noqa
        """Builds all required python binary extensions of the project."""
        if os.getenv("PRE_COMMIT"):
            return

        include_dirs = []
        library_dirs = []

        pkg_config = None
        if _cmd_exists(os.environ.get("PKG_CONFIG", "pkg-config")):
            pkg_config = _pkg_config

        for root_name, lib_name in {
            "LIBHEIF_ROOT": ("libheif", "heif"),
        }.items():
            root = globals()[root_name]

            if root is None and root_name in os.environ:
                prefix = os.environ[root_name]
                root = (os.path.join(prefix, "lib"), os.path.join(prefix, "include"))

            if root is None and pkg_config:
                if isinstance(lib_name, tuple):
                    for lib_name2 in lib_name:
                        print(f"Looking for `{lib_name2}` using pkg-config.")
                        root = pkg_config(lib_name2)
                        if root:
                            break
                else:
                    print(f"Looking for `{lib_name}` using pkg-config.")
                    root = pkg_config(lib_name)

            if isinstance(root, tuple):
                lib_root, include_root = root
            else:
                lib_root = include_root = root

            if lib_root is not None:
                if not isinstance(lib_root, (tuple, list)):
                    lib_root = (lib_root,)
                for lib_dir in lib_root:
                    self._add_directory(library_dirs, lib_dir)
            if include_root is not None:
                if not isinstance(include_root, (tuple, list)):
                    include_root = (include_root,)
                for include_dir in include_root:
                    self._add_directory(include_dirs, include_dir)

        # respect CFLAGS/CPPFLAGS/LDFLAGS
        for k in ("CFLAGS", "CPPFLAGS", "LDFLAGS"):
            if k in os.environ:
                for match in finditer(r"-I([^\s]+)", os.environ[k]):
                    self._add_directory(include_dirs, match.group(1))
                for match in finditer(r"-L([^\s]+)", os.environ[k]):
                    self._add_directory(library_dirs, match.group(1))

        # include, rpath, if set as environment variables
        for k in ("C_INCLUDE_PATH", "CPATH", "INCLUDE"):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    self._add_directory(include_dirs, d)

        for k in ("LD_RUN_PATH", "LIBRARY_PATH", "LIB"):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    self._add_directory(library_dirs, d)

        self._add_directory(include_dirs, os.path.join(sys.prefix, "include"))
        self._add_directory(library_dirs, os.path.join(sys.prefix, "lib"))

        if sys.platform.lower() == "win32":
            # Currently only MSYS2 is supported for Windows systems. Do a PR if you need support for anything else.
            include_path_prefix = os.getenv("MSYS2_PREFIX")
            if include_path_prefix is None:
                include_path_prefix = "C:\\msys64\\mingw64"
                warn(
                    f"MSYS2_PREFIX environment variable is not set. Assuming MSYS2_PREFIX={include_path_prefix}",
                    stacklevel=1,
                )

            if not os.path.isdir(include_path_prefix):
                raise ValueError("MSYS2 not found and `MSYS2_PREFIX` is not set or is invalid.")

            library_dir = os.path.join(include_path_prefix, "lib")
            # See comment a few lines below. We can't include MSYS2 directory before compiler directories.
            # self._add_directory(include_dirs, path.join(include_path_prefix, "include"))
            self._add_directory(library_dirs, library_dir)
            lib_export_file = Path(os.path.join(library_dir, "libheif.dll.a"))
            lib_lib_file = Path(os.path.join(library_dir, "libheif.lib"))
            if lib_export_file.is_file() and not lib_lib_file.is_file():
                print(f"Copying {lib_export_file} to {lib_lib_file}")
                copy(lib_export_file, lib_lib_file)
            else:
                warn("If you build this with MSYS2, you should not see this warning.", stacklevel=1)

            # on Windows, we include "root" of the project instead of MSYS2 directory.
            # Including MSYS2 directory leads to compilation errors, theirs `stdio.h` and other files are different.
            # ATTENTION: If someone knows how without hacks include MSYS2 directory as last directory in list - help!
            self.compiler.include_dirs.append(os.path.dirname(os.path.abspath(__file__)))

            if PLATFORM_MINGW:
                self._update_extension("_pillow_heif", ["heif"], extra_compile_args=["-O3", "-Werror"])
            else:
                self._update_extension(
                    "_pillow_heif", ["libheif"], extra_compile_args=["/d2FH4-", "/WX"], extra_link_args=["/WX"]
                )
        elif sys.platform.lower() == "darwin":
            try:  # if Homebrew is installed, use its lib and include directories
                homebrew_prefix = subprocess.check_output(["brew", "--prefix"]).strip().decode("latin1")
            except Exception:  # noqa # pylint: disable=broad-except
                homebrew_prefix = None  # Homebrew isn't installed
            if homebrew_prefix:
                # add Homebrew's "include" and "lib" directories
                self._add_directory(library_dirs, os.path.join(homebrew_prefix, "lib"))
                self._add_directory(include_dirs, os.path.join(homebrew_prefix, "include"))

            # fink installation directories
            self._add_directory(library_dirs, "/sw/lib")
            self._add_directory(include_dirs, "/sw/include")
            # darwin ports installation directories
            self._add_directory(library_dirs, "/opt/local/lib")
            self._add_directory(include_dirs, "/opt/local/include")

            sdk_path = self._get_macos_sdk_path()
            if sdk_path:
                self._add_directory(library_dirs, os.path.join(sdk_path, "usr", "lib"))
                self._add_directory(include_dirs, os.path.join(sdk_path, "usr", "include"))

            self._update_extension("_pillow_heif", ["heif"], extra_compile_args=["-O3", "-Werror"])
        else:  # let's assume it's some kind of linux
            # this old code waiting for refactoring, when time comes.
            self._add_directory(include_dirs, "/usr/local/include")
            self._add_directory(include_dirs, "/usr/include")
            self._add_directory(library_dirs, "/usr/local/lib")
            self._add_directory(library_dirs, "/usr/lib64")
            self._add_directory(library_dirs, "/usr/lib")
            self._add_directory(library_dirs, "/lib")

            self._update_extension("_pillow_heif", ["heif"], extra_compile_args=["-O3", "-Werror"])

        self.compiler.library_dirs = library_dirs + self.compiler.library_dirs
        self.compiler.include_dirs = include_dirs + self.compiler.include_dirs

        heif_include = self._find_include_dir("libheif", "heif.h")
        if not heif_include:
            raise RequiredDependencyException("libheif")

        build_ext.build_extensions(self)

    def _update_extension(self, name: str, libraries, extra_compile_args=None, extra_link_args=None) -> None:
        for extension in self.extensions:
            if extension.name == name:
                extension.libraries += libraries
                if extra_compile_args is not None:
                    extension.extra_compile_args += extra_compile_args
                if extra_link_args is not None:
                    extension.extra_link_args += extra_link_args

    def _find_include_dir(self, dirname: str, include: str):
        for directory in self.compiler.include_dirs:
            print(f"Checking for include file '{include}' in '{directory}'")
            result_path = os.path.join(directory, include)
            if os.path.isfile(result_path):
                print(f"Found '{include}' in '{directory}'")
                return result_path
            subdir = os.path.join(directory, dirname)
            print(f"Checking for include file '{include}' in '{subdir}'")
            result_path = os.path.join(subdir, include)
            if os.path.isfile(result_path):
                print(f"Found '{include}' in '{subdir}'")
                return result_path
        return ""

    @staticmethod
    def _add_directory(paths: list[str], subdir: str | None):
        if subdir:
            subdir = os.path.realpath(subdir)
            if os.path.isdir(subdir) and subdir not in paths:
                paths.append(subdir)

    @staticmethod
    def _get_macos_sdk_path():
        try:
            sdk_path = subprocess.check_output(["xcrun", "--show-sdk-path"]).strip().decode("latin1")
        except Exception:  # noqa  # pylint: disable=broad-exception-caught
            sdk_path = None
        if (
            not sdk_path
            or sdk_path
            == "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
        ):
            commandlinetools_sdk_path = "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
            if os.path.exists(commandlinetools_sdk_path):
                sdk_path = commandlinetools_sdk_path
        return sdk_path


try:
    if os.getenv("READTHEDOCS", "False") == "True":
        setup(version=get_version())
    else:
        setup(
            version=get_version(),
            cmdclass={"build_ext": PillowHeifBuildExt},
            ext_modules=[Extension("_pillow_heif", ["pillow_heif/_pillow_heif.c"])],
            zip_safe=not PLATFORM_MINGW,
        )
except RequiredDependencyException as err:
    MSG = f"""

The headers or library files could not be found for {err},
a required dependency when compiling Pillow-Heif from source.

Please see the install instructions at:
   https://pillow-heif.readthedocs.io/en/latest/installation.html

"""
    sys.stderr.write(MSG)
    raise RequiredDependencyException(MSG) from None
