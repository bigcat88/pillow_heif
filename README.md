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

Library to work with HEIF files and an add-on for Pillow.
Using the [libheif](https://github.com/strukturag/libheif) library via [CFFI](https://cffi.readthedocs.io).

**Wheels table:**

|               | macOS Intel | macOS Silicon | Windows 64bit | musllinux | manylinux |
|---------------|:-----------:|:-------------:|:-------------:|:---------:|:---------:|
| CPython 3.6   |     N/A     |      N/A      |      N/A      |     ✅     |     ✅     |
| CPython 3.7   |      ✅      |      N/A      |       ✅       |     ✅     |     ✅     |
| CPython 3.8   |      ✅      |      N/A      |       ✅       |     ✅     |     ✅     |
| CPython 3.9   |      ✅      |       ✅       |       ✅       |     ✅     |     ✅     |
| CPython 3.10  |      ✅      |       ✅       |       ✅       |     ✅     |     ✅     |
| PyPy 3.7 v7.3 |     N/A     |      N/A      |      N/A      |    N/A    |     ✅     |
| PyPy 3.8 v7.3 |     N/A     |      N/A      |      N/A      |    N/A    |     ✅     |
| PyPy 3.9 v7.3 |     N/A     |      N/A      |      N/A      |    N/A    |    N/A    |

Note: **CPython** **musllinux**/**manylinux** wheels for **i686**, **x64_86** and **aarch64**(arm8)

#### **_Versions 0.2.X will be last to support Python 3.6_**

**Pull requests are greatly welcome.**

## Installation
(Recommended) From [PyPi](https://pypi.org/project/pillow-heif/):

```bash
python3 -m pip install pillow_heif
```

### [Building from source](https://github.com/bigcat88/pillow_heif/blob/master/docs/BUILDING.md)

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

if not pillow_heif.is_supported('ABC.HEIC'):
  exit(0)
heif_file = pillow_heif.read_heif('ABC.HEIC')
for img in heif_file:       # you still can use it without iteration, like before.
    image = Image.frombytes(
        img.mode,
        img.size,
        img.data,
        'raw',
        img.mode,
        img.stride,
    )
```
### [More examples](https://github.com/bigcat88/pillow_heif/tree/master/examples)


### The HeifImageFile object (as Pillow plugin)
The returned `HeifImageFile` by `Pillow` function `Image.open` has the following additional properties beside regular:
* `info` dictionary keys:
  * `brand` - value from int enum `HeifBrand`.
  * `exif` - exif data or `None`.
  * `metadata` - is a list of dictionaries with `type` and `data` keys, excluding `exif`. May be empty.
  * `color_profile` - is a dictionary with `type` and `data` keys. May be empty.
  * `icc_profile` - contains data and present only when file has `ICC` color profile(`prof` or `rICC`).
  * `nclx_profile` - contains data and present only when file has `NCLX` color profile.

### An UndecodedHeifFile object
The returned `UndecodedHeifFile` by function `open_heif` has the following properties:

* `size` - the size of the image as a `(width, height)` tuple of integers.
* `has_alpha` - is a boolean indicating the presence of an alpha channel.
* `mode` - the image mode, e.g. 'RGB' or 'RGBA'.
* `bit_depth` - the number of bits in each component of a pixel.
* `data` - the raw decoded file data, as bytes. Contains `None` until `load` method is called.
* `stride` - the number of bytes in a row of decoded file data. Contains `None` until `load` method is called.
* `id` - id of image, will be needed for encoding operations later.
* `main` - is a boolean indicating, if it is a default picture.
* `info` dictionary with the same content as in `HeifImageFile.info`.
* `thumbnails` - list of `HeifThumbnail` or `UndecodedHeifThumbnail` classes.
* `top_lvl_images` - list of `UndecodedHeifFile` or `HeifFile` classes, excluding main image.
* class supports `len` and `iter` methods:
  * `len` - returns number of top level images including main.
  * `iter` - returns a generator to iterate through all images, first image will be main.

### The HeifFile object

`HeifFile` can be obtained by calling `load` method of `UndecodedHeifFile` or by calling `read_heif` function.
`HeifFile` has all properties of `UndecodedHeifFile` plus filled `data` and `stride`.

## Thumbnails
To enable thumbnails, set `thumbnails` property in `options` to True:
```python3
import pillow_heif

pillow_heif.options().thumbnails = True
pillow_heif.options().thumbnails_autoload = True # if you wish
# or
pillow_heif.register_heif_opener(thumbnails=True, thumbnails_autoload=True)
```

### The UndecodedHeifThumbnail object
* `size` - the size of the image as a `(width, height)` tuple of integers.
* `has_alpha` - is a boolean indicating the presence of an alpha channel.
* `mode` - the image mode, e.g. 'RGB' or 'RGBA'.
* `bit_depth` - the number of bits in each component of a pixel.
* `data` - the raw decoded file data, as bytes. Contains `None` until `load` method is called.
* `stride` - the number of bytes in a row of decoded file data. Contains `None` until `load` method is called.
* `id` - id of thumbnail, will be needed for encoding operations later.

### The HeifThumbnail object

You can enable thumbnail autoload by setting `thumbnails_autoload` property to `True`.

Also `HeifThumbnail` can be obtained by calling `load` method of `UndecodedHeifThumbnail`, `UndecodedHeifFile` or `HeifImageFile`.

`HeifThumbnail` has all properties of `UndecodedHeifThumbnail` plus filled `data` and `stride`.
