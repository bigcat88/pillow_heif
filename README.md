# pillow_heif

![analysis](https://github.com/bigcat88/pillow_heif/actions/workflows/analysis-coverage.yml/badge.svg)
![build](https://github.com/bigcat88/pillow_heif/actions/workflows/create-release-draft.yml/badge.svg)
![published](https://github.com/bigcat88/pillow_heif/actions/workflows/publish-pypi.yaml/badge.svg)
[![codecov](https://codecov.io/gh/bigcat88/pillow_heif/branch/master/graph/badge.svg?token=JY64F2OL6V)](https://codecov.io/gh/bigcat88/pillow_heif)
![style](https://img.shields.io/badge/code%20style-black-000000.svg)

![PythonVersion](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)
![impl](https://img.shields.io/pypi/implementation/pillow_heif)
[![Downloads](https://static.pepy.tech/personalized-badge/pillow-heif?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/pillow-heif)
[![Downloads](https://static.pepy.tech/personalized-badge/pillow-heif?period=month&units=international_system&left_color=grey&right_color=orange&left_text=Downloads/Month)](https://pepy.tech/project/pillow-heif)
![pypi](https://img.shields.io/pypi/v/pillow_heif.svg)

![Mac OS](https://img.shields.io/badge/mac%20os-FCC624?style=for-the-badge&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-0078D6.svg?style=for-the-badge&logo=alpine-linux&logoColor=white)

A HEIF/HEIC/AVIF add-on for Pillow using the [libheif](https://github.com/strukturag/libheif) library via [CFFI](https://cffi.readthedocs.io).

**Wheels table:**

|               | macOS Intel | macOS Silicon | Windows 64bit | musllinux | manylinux |
|---------------|:-----------:|:-------------:|:-------------:|:---------:|:---------:|
| CPython 3.6   |     N/A     |      N/A      |      N/A      |     ✅     |     ✅     |
| CPython 3.7   |      ✅      |      N/A      |       ✅       |     ✅     |     ✅     |
| CPython 3.8   |      ✅      |      N/A      |       ✅       |     ✅     |     ✅     |
| CPython 3.9   |      ✅      |       ✅       |       ✅       |     ✅     |     ✅     |
| CPython 3.10  |      ✅      |       ✅       |       ✅       |     ✅     |     ✅     |
| PyPy 3.7 v7.3 |     N/A     |      N/A      |      N/A      |     ✅     |     ✅     |
| PyPy 3.8 v7.3 |     N/A     |      N/A      |      N/A      |     ✅     |     ✅     |

#### **_Versions 0.2.9 will be last to support Python 3.6._**

**Pull requests are greatly welcome.**

## Installation
(Recommended) From [PyPi](https://pypi.org/project/pillow-heif/):

```bash
pip3 install pillow_heif
```


## Installation from source

### Linux

#### Debian(Ubuntu):
```bash
sudo apt install -y python3-pip libtool git cmake
sudo -H python3 -m pip install --upgrade pip
sudo -H python3 -m pip install pillow_heif
```


#### Alpine:
```bash
sudo apk --no-cache add py3-pip python3-dev libtool git gcc m4 perl alpine-sdk cmake
sudo apk --no-cache add fribidi-dev harfbuzz-dev jpeg-dev lcms2-dev openjpeg-dev
sudo -H python3 -m pip install --upgrade pip
sudo -H python3 -m pip install pillow_heif
```

See [build_libs_linux](https://github.com/bigcat88/pillow_heif/blob/master/libheif/build_libs.py) for additional info what will happen during installing from source.

Notes:

1. Building for first time will take a long time, if in your system `cmake` version `>=3.16.1` is not present.
2. Arm7(32 bit): On Alpine you need additionally install `aom` and `aom-dev` packages.
3. Arm7(32 bit): On Ubuntu(22.04+) you need additionally install `libaom-dev` package.
4. Arm7(32 bit): Ubuntu < 22.04 is not supported currently.

### MacOS
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install x265 libjpeg libde265 libheif
pip3 install --no-binary pillow_heif
```

### Windows
```bat
vcpkg install aom libheif --triplet=x64-windows
VCPKG_PREFIX="path_to:vcpkg/installed/x64-windows"
pip3 install --no-binary pillow_heif
```

## Example of use as opener
```python3
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

image = Image.open('image.heic')
image.load()
```

## Example of use as reader
```python3
from PIL import Image
import pillow_heif

heif_file = pillow_heif.read_heif('ABC.HEIC')
image = Image.frombytes(
    heif_file.mode,
    heif_file.size,
    heif_file.data,
    'raw',
    heif_file.mode,
    heif_file.stride,
)
```

### The HeifImageFile object (as Pillow plugin)
The returned `HeifImageFile` by `Pillow` function `Image.open` has the following additional properties beside regular:
* `metadata` - the same as in an `UndecodedHeifFile.metadata`.
* `info["exif"]` - the same as in an `UndecodedHeifFile.exif`. If there is no exif, then absent.
* `info["color_profile"]` - the same as in an `UndecodedHeifFile.color_profile`. If there is no profile, then absent.
* `info["icc_profile"]` - contains data and present only when file has `ICC` color profile(`prof` or `rICC`).
* `info["nclx_profile"]` - contains data and present only when file has `NCLX` color profile.

### An UndecodedHeifFile object
The returned `UndecodedHeifFile` by function `open_heif` has the following properties:

* `size` - the size of the image as a `(width, height)` tuple of integers.
* `brand` - value from int enum `HeifBrand`.
* `has_alpha`  - (bool)presence of alpha channel.
* `mode` - the image mode, e.g. 'RGB' or 'RGBA'.
* `bit_depth` - the number of bits in each component of a pixel.
* `exif` - exif data or None.
* `metadata` - a list of metadata dictionaries, excluding `exif`.
* `color_profile` - `None` or a color profile dictionary with `type` and `data` keys.
* `data` - the raw decoded file data, as bytes. Contains `None` until `load` method is called.
* `stride` - the number of bytes in a row of decoded file data. Contains `None` until `load` method is called.

### The HeifFile object

`HeifFile` can be obtained by calling `load` method of `UndecodedHeifFile` or by calling `read_heif` function.
`HeifFile` has all properties of `UndecodedHeifFile` plus filled `data` and `stride`.
