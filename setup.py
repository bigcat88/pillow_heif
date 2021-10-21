from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pillow_heif",
    version="0.1.3",
    packages=["pillow_heif"],
    install_requires=["cffi>=1.0.0", "pillow"],
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["libheif/build.py:ffibuilder"],
    author="Alexander Piskun",
    author_email="bigcat88@users.noreply.github.com",
    description="Python 3.6+ interface to libheif library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="pillow heif heic",
    url="https://github.com/bigcat88/pillow_heif",
    license="Apache Software License",
)
