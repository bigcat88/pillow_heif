#!/usr/bin/env python
from setuptools import setup
from wheel.bdist_wheel import bdist_wheel


class Abi3Wheels(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()
        if python.startswith("cp"):
            return "cp36", "abi3", plat
        return python, abi, plat


def get_version():
    version_file = "pillow_heif/_version.py"
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


setup(
    version=get_version(),
    cffi_modules=["libheif/build.py:ffi"],
    cmdclass={"bdist_wheel": Abi3Wheels},
)
