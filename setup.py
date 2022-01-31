#!/usr/bin/env python
from setuptools import setup


def get_version():
    version_file = "pillow_heif/_version.py"
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    install_requirements = [line.rstrip() for line in fh.readlines()]

with open("requirements_dev.txt", "r", encoding="utf-8") as fh:
    test_requirements = [line.rstrip() for line in fh.readlines()]

setup(
    name="pillow_heif",
    version=get_version(),
    packages=["pillow_heif"],
    install_requires=["cffi>=1.14.0", *install_requirements],
    setup_requires=["cffi>=1.14.0"],
    cffi_modules=["libheif/build.py:ffibuilder"],
    author="Alexander Piskun",
    author_email="bigcat88@users.noreply.github.com",
    description="Python 3.7+ interface to libheif library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    test_suite="tests",
    tests_require=test_requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
    license="Apache-2.0",
    keywords="pillow heif heic avif",
    url="https://github.com/bigcat88/pillow_heif",
    zip_safe=False,
)
