#!/usr/bin/env python
from setuptools import setup
from wheel.bdist_wheel import bdist_wheel


class WheelsABI3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()
        if python.startswith("cp"):
            python = "cp36"
            abi = "abi3"
            if plat.startswith("macosx"):
                python = "cp37" if plat.find("x86_64") != -1 else "cp38"
            elif plat.startswith("win"):
                python = "cp37"
            elif plat == "linux_armv7l":
                python = "cp38"
        return python, abi, plat


def get_version():
    version_file = "pillow_heif/_version.py"
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


setup(
    version=get_version(),
    cffi_modules=["libheif/build.py:ffi"],
    cmdclass={"bdist_wheel": WheelsABI3},
)
