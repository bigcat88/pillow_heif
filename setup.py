#!/usr/bin/env python
from setuptools import setup


def get_version():
    version_file = "pillow_heif/_version.py"
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


setup(
    version=get_version(),
    cffi_modules=["libheif/build.py:ffi"],
)
