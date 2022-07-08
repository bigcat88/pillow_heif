#!/usr/bin/env python
from setuptools import setup
from wheel.bdist_wheel import bdist_wheel

# class WheelsABI3(bdist_wheel):
#     def get_tag(self):
#         python, abi, plat = super().get_tag()
#         if python.startswith("cp"):
#             python = "cp36"
#             abi = "abi3"
#             if plat.startswith("macosx"):
#                 python = "cp37" if plat.find("x86_64") != -1 else "cp39"
#             elif plat.startswith("win"):
#                 python = "cp37"
#             elif plat == "linux_armv7l":
#                 python = "cp38"
#         return python, abi, plat


class WheelNoneABI(bdist_wheel):
    def finalize_options(self):
        bdist_wheel.finalize_options(self)
        self.root_is_pure = False  # noqa

    def get_tag(self):
        python, abi, plat = bdist_wheel.get_tag(self)
        return "py3", "none", plat


def get_version():
    version_file = "pillow_heif/_version.py"
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


setup(
    version=get_version(),
    cffi_modules=["libheif/build.py:ffi"],
    cmdclass={"bdist_wheel": WheelNoneABI},
    # cmdclass={"bdist_wheel": WheelsABI3},
)
