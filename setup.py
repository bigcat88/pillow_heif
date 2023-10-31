#!/usr/bin/env python
"""Script to build wheel."""
import os
import re
import subprocess
import sys
from pathlib import Path
from re import finditer
from shutil import copy
from typing import List
from warnings import warn

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

from libheif import linux_build_libs


def get_version():
    """Returns version of the project."""
    version_file = "pillow_heif/_version.py"
    exec(compile(Path(version_file).read_text(encoding="utf-8"), version_file, "exec"))  # pylint: disable=exec-used
    return locals()["__version__"]


def _cmd_exists(cmd: str) -> bool:
    """Checks if specified command exists on the machine."""
    if "PATH" not in os.environ:
        return False
    return any(os.access(os.path.join(path, cmd), os.X_OK) for path in os.environ["PATH"].split(os.pathsep))


def _pkg_config(name):
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
            # if not DEBUG:
            #     command_libs.append("--silence-errors")
            #     command_cflags.append("--silence-errors")
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

    def build_extensions(self):  # noqa pylint: disable=too-many-branches disable=too-many-statements
        """Builds all required python binary extensions of the project."""
        if os.getenv("PRE_COMMIT"):
            return

        include_dirs = []
        library_dirs = []

        pkg_config = None
        if _cmd_exists(os.environ.get("PKG_CONFIG", "pkg-config")):
            pkg_config = _pkg_config

        root = None
        libheif_found = False
        if pkg_config:
            for lib_name in ("heif", "libheif"):
                print(f"Looking for `{lib_name}` using pkg-config.")
                root = pkg_config(lib_name)
                if root:
                    print(f"Found `{lib_name}` using pkg-config: {root}")
                    libheif_found = True
                    break

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
                    f"MSYS2_PREFIX environment variable is not set. Assuming `MSYS2_PREFIX={include_path_prefix}`",
                    stacklevel=1,
                )

            if not os.path.isdir(include_path_prefix):
                raise ValueError("MSYS2 not found and `MSYS2_PREFIX` is not set or is invalid.")

            library_dir = os.path.join(include_path_prefix, "lib")
            # See comment a few lines below. We can't include MSYS2 directory before compiler directories :(
            # self._add_directory(include_dirs, path.join(include_path_prefix, "include"))
            self._add_directory(library_dirs, library_dir)
            lib_export_file = Path(os.path.join(library_dir, "libheif.dll.a"))
            if lib_export_file.is_file():
                copy(lib_export_file, os.path.join(library_dir, "libheif.lib"))
            else:
                warn("If you build this with MSYS2, you should not see this warning.", stacklevel=1)

            # on Windows, we include "root" of the project instead of MSYS2 directory.
            # Including MSYS2 directory leads to compilation errors, theirs `stdio.h` and other files are different.
            # ATTENTION: If someone knows how without hacks include MSYS2 directory as last directory in list - help!
            self.compiler.include_dirs.append(os.path.dirname(os.path.abspath(__file__)))

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

            self._update_extension("_pillow_heif", ["heif"], extra_compile_args=["-Ofast", "-Werror"])
        else:  # let's assume it's some kind of linux
            # this old code waiting for refactoring, when time comes.
            self._add_directory(include_dirs, "/usr/local/include")
            self._add_directory(include_dirs, "/usr/include")
            self._add_directory(library_dirs, "/usr/local/lib")
            self._add_directory(library_dirs, "/usr/lib64")
            self._add_directory(library_dirs, "/usr/lib")
            self._add_directory(library_dirs, "/lib")

            if not libheif_found:
                include_path_prefix = linux_build_libs.build_libs()  # this needs a rework in the future
                self._add_directory(library_dirs, os.path.join(include_path_prefix, "lib"))
                self._add_directory(include_dirs, os.path.join(include_path_prefix, "include"))

            self._update_extension("_pillow_heif", ["heif"], extra_compile_args=["-Ofast", "-Werror"])

        self.compiler.library_dirs = library_dirs + self.compiler.library_dirs
        self.compiler.include_dirs = include_dirs + self.compiler.include_dirs

        build_ext.build_extensions(self)

    def _update_extension(self, name, libraries, extra_compile_args=None, extra_link_args=None):
        for extension in self.extensions:
            if extension.name == name:
                extension.libraries += libraries
                if extra_compile_args is not None:
                    extension.extra_compile_args += extra_compile_args
                if extra_link_args is not None:
                    extension.extra_link_args += extra_link_args

    @staticmethod
    def _add_directory(paths: List, subdir):
        if subdir:
            subdir = os.path.realpath(subdir)
            if os.path.isdir(subdir) and subdir not in paths:
                paths.append(subdir)


if os.getenv("READTHEDOCS", "False") == "True":
    setup(version=get_version())
else:
    setup(
        version=get_version(),
        cmdclass={"build_ext": PillowHeifBuildExt},
        ext_modules=[Extension("_pillow_heif", ["pillow_heif/_pillow_heif.c"])],
    )
