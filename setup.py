#!/usr/bin/env python
"""Script to build wheel"""
import sys
from os import environ, getenv, path
from pathlib import Path
from re import finditer
from shutil import copy
from subprocess import check_output
from typing import List
from warnings import warn

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

from libheif import linux_build_libs


def get_version():
    version_file = "pillow_heif/_version.py"
    with open(version_file, encoding="utf-8") as f:
        exec(compile(f.read(), version_file, "exec"))  # pylint: disable=exec-used
    return locals()["__version__"]


class PillowHeifBuildExt(build_ext):
    """This class is based on the Pillow setup method"""

    def build_extensions(self):  # pylint: disable=too-many-branches disable=too-many-statements
        if getenv("PRE_COMMIT"):
            return

        include_dirs = []
        library_dirs = []

        # respect CFLAGS/CPPFLAGS/LDFLAGS
        for k in ("CFLAGS", "CPPFLAGS", "LDFLAGS"):
            if k in environ:
                for match in finditer(r"-I([^\s]+)", environ[k]):
                    self._add_directory(include_dirs, match.group(1))
                for match in finditer(r"-L([^\s]+)", environ[k]):
                    self._add_directory(library_dirs, match.group(1))

        # include, rpath, if set as environment variables
        for k in ("C_INCLUDE_PATH", "CPATH", "INCLUDE"):
            if k in environ:
                for d in environ[k].split(path.pathsep):
                    self._add_directory(include_dirs, d)

        for k in ("LD_RUN_PATH", "LIBRARY_PATH", "LIB"):
            if k in environ:
                for d in environ[k].split(path.pathsep):
                    self._add_directory(library_dirs, d)

        self._add_directory(include_dirs, path.join(sys.prefix, "include"))
        self._add_directory(library_dirs, path.join(sys.prefix, "lib"))

        if sys.platform.lower() == "win32":
            # Currently only MSYS2 is supported for Windows systems. Do a PR if you need support for anything else.
            include_path_prefix = getenv("MSYS2_PREFIX")
            if include_path_prefix is None:
                include_path_prefix = "C:\\msys64\\mingw64"
                warn(f"MSYS2_PREFIX environment variable is not set. Assuming `MSYS2_PREFIX={include_path_prefix}`")

            if not path.isdir(include_path_prefix):
                raise ValueError("MSYS2 not found and `MSYS2_PREFIX` is not set or is invalid.")

            library_dir = path.join(include_path_prefix, "lib")
            # See comment a few lines below. We can't include MSYS2 directory before compiler directories :(
            # self._add_directory(include_dirs, path.join(include_path_prefix, "include"))
            self._add_directory(library_dirs, library_dir)
            lib_export_file = Path(path.join(library_dir, "libheif.dll.a"))
            if lib_export_file.is_file():
                copy(lib_export_file, path.join(library_dir, "libheif.lib"))
            else:
                warn("If you build this with MSYS2, you should not see this warning.")

            # on Windows, we include root of project instead of MSYS2 directory.
            # Including MSYS2 directory leads to compilation errors, theirs `stdio.h` and others files are different.
            # ATTENTION: If someone know how without hacks include MSYS2 directory as last directory in list - help!
            self.compiler.include_dirs.append(path.dirname(path.abspath(__file__)))

            self._update_extension(
                "_pillow_heif", ["libheif"], extra_compile_args=["/d2FH4-", "/WX"], extra_link_args=["/WX"]
            )
        elif sys.platform.lower() == "darwin":
            try:  # if Homebrew is installed, use its lib and include directories
                homebrew_prefix = check_output(["brew", "--prefix"]).strip().decode("latin1")
            except Exception:  # noqa # pylint: disable=broad-except
                homebrew_prefix = None  # Homebrew not installed
            if homebrew_prefix:
                # add Homebrew's include and lib directories
                self._add_directory(library_dirs, path.join(homebrew_prefix, "lib"))
                self._add_directory(include_dirs, path.join(homebrew_prefix, "include"))

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

            include_path_prefix = linux_build_libs.build_libs()  # this need a rework in the future
            self._add_directory(library_dirs, path.join(include_path_prefix, "lib"))
            self._add_directory(include_dirs, path.join(include_path_prefix, "include"))

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
            subdir = path.realpath(subdir)
            if path.isdir(subdir) and subdir not in paths:
                paths.append(subdir)


setup(
    version=get_version(),
    cmdclass={"build_ext": PillowHeifBuildExt},
    ext_modules=[Extension("_pillow_heif", ["pillow_heif/_pillow_heif.c"])],
)
