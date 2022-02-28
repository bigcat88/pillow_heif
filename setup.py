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
    install_requires=install_requirements,
    setup_requires=["cffi>=1.15.0", "setuptools>=41.2.0"],
    cffi_modules=["libheif/build.py:ffi"],
    author="Alexander Piskun",
    author_email="bigcat88@users.noreply.github.com",
    description="Python 3.6+ interface to libheif library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    test_suite="tests",
    tests_require=test_requirements,
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Multimedia :: Graphics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    license="Apache-2.0",
    keywords="pillow heif heic avif",
    url="https://github.com/bigcat88/pillow_heif",
    zip_safe=False,
)
