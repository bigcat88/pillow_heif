# pillow-heif

![analysis](https://github.com/bigcat88/pillow_heif/actions/workflows/analysis-coverage.yml/badge.svg)
![build](https://github.com/bigcat88/pillow_heif/actions/workflows/create-release-draft.yml/badge.svg)
![wheels test](https://github.com/bigcat88/pillow_heif/actions/workflows/test-wheels.yaml/badge.svg)
[![codecov](https://codecov.io/gh/bigcat88/pillow_heif/branch/master/graph/badge.svg?token=JY64F2OL6V)](https://codecov.io/gh/bigcat88/pillow_heif)
![style](https://img.shields.io/badge/code%20style-black-000000.svg)

![PythonVersion](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)
![impl](https://img.shields.io/pypi/implementation/pillow_heif)
![pypi](https://img.shields.io/pypi/v/pillow_heif.svg)
[![Downloads](https://static.pepy.tech/personalized-badge/pillow-heif?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/pillow-heif)
[![Downloads](https://static.pepy.tech/personalized-badge/pillow-heif?period=month&units=international_system&left_color=grey&right_color=orange&left_text=Downloads/Month)](https://pepy.tech/project/pillow-heif)

![Mac OS](https://img.shields.io/badge/mac%20os-FCC624?style=for-the-badge&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-0078D6.svg?style=for-the-badge&logo=alpine-linux&logoColor=white)


Library to work with HEIF files and an add-on for Pillow.
Using the [libheif](https://github.com/strukturag/libheif) via [CFFI](https://cffi.readthedocs.io).

Here last release of **0.1** version: [tag](https://github.com/bigcat88/pillow_heif/tree/v0.1.11)

## Example of use as pillow plugin.
```python3
from PIL import Image, ImageSequence
from pillow_heif import register_heif_opener

register_heif_opener()

image = Image.open('images/input.heic')
for i, frame in enumerate(ImageSequence.Iterator(image)):
    rotated = frame.rotate(13)
    rotated.save(f'rotated_frame{i}.heic', quality=90)
exit(0)
```

## Standalone example use
```python3
from PIL import Image
import pillow_heif

if pillow_heif.is_supported('input.heic'):
    heif_file = pillow_heif.open_heif('input.heic')
    for img in heif_file:  # you still can use it without iteration, like before.
        img.scale(1024, 768) # `libheif` does not provide much operations, that can be done on image, so just scaling it.
    # get save mask and set thumb_box=-1 to ignore all thumbs image have.
    save_mask = heif_file.get_img_thumb_mask_for_save(pillow_heif.HeifSaveMask.SAVE_ALL, thumb_box=-1)
    heif_file.add_thumbs_to_mask(save_mask, [768, 512, 256]) # add three new thumbnail boxes.
    # default quality is probably ~77 in x265, set it a bit lower and specify `save mask`.
    heif_file.save('output.heic', quality=70, save_mask=save_mask)
    exit(0)
```
### [More examples](https://github.com/bigcat88/pillow_heif/tree/master/examples)

## Installation
From [PyPi](https://pypi.org/project/pillow-heif/) or [Build from source](https://github.com/bigcat88/pillow_heif/blob/master/docs/BUILDING.md)

| **_Wheels table_** | macOS<br/>Intel | macOS<br/>Silicon | Windows<br/>64bit | musllinux* | manylinux* |
|--------------------|:---------------:|:-----------------:|:-----------------:|:----------:|:----------:|
| CPython 3.6        |       N/A       |        N/A        |        N/A        |     ✅      |     ✅      |
| CPython 3.7        |        ✅        |        N/A        |         ✅         |     ✅      |     ✅      |
| CPython 3.8        |        ✅        |        N/A        |         ✅         |     ✅      |     ✅      |
| CPython 3.9        |        ✅        |         ✅         |         ✅         |     ✅      |     ✅      |
| CPython 3.10       |        ✅        |         ✅         |         ✅         |     ✅      |     ✅      |
| PyPy 3.7 v7.3      |        ✅        |        N/A        |        N/A        |    N/A     |     ✅      |
| PyPy 3.8 v7.3      |        ✅        |        N/A        |        N/A        |    N/A     |     ✅      |

&ast; **i686**, **x86_64**, **aarch64** wheels.

#### **_Versions 0.2.X will be last to support Python 3.6_**

### More documentation will arrive soon, before 0.3.0 version...

### The HeifImageFile object (as Pillow plugin)
The returned `HeifImageFile` by `Pillow` function `Image.open` has the following additional properties beside regular:
* `info` dictionary keys:
  * `main` - boolean indication if this a main image in sequence.
  * `brand` - value from int enum `HeifBrand`.
  * `exif` - exif data or `None`.
  * `metadata` - is a list of dictionaries with `type` and `data` keys, excluding `exif`. May be empty.
  * `icc_profile` - contains data and present only when file has `ICC` color profile(`prof` or `rICC`).
  * `nclx_profile` - contains data and present only when file has `NCLX` color profile.
  * `img_id` - id of image, needed for encoding operations.

### The HeifFile object
The returned `HeifFile` by function `open_heif` or `from_pillow` has the following properties:

* `size`, `has_alpha`, `mode`, `bit_depth`, `data`, `stride`, `info`, etc - properties that points to main `HeifImage`
* class supports `len`, `iter` and `__getitem__`:
  * `len` - returns number of top level images including main.
  * `iter` - returns a generator to iterate through all images, first image will be main.
  * `__getitem__` - returns image by index, image with index=0 is main.
* other useful class methods:
  * `thumbnails_all` - returns an iterator to access thumbnails for all images in file.
  * `add_from_pillow` - add image(s) from pillow :)
  * `add_from_heif` - add image(s) from another `HeifFile`.
  * `save` - saves `HeifFile` to `fp` that can be `Path` or `BytesIO`.

### The HeifImage object

* `size` - the size of the image as a `(width, height)` tuple of integers.
* `has_alpha` - is a boolean indicating the presence of an alpha channel.
* `mode` - the image mode, e.g. 'RGB' or 'RGBA'.
* `bit_depth` - the number of bits in each component of a pixel.
* `data` - the raw decoded file data, as bytes.
* `stride` - the number of bytes in a row of decoded file data.
* `info` - same dictionary as in `HeifImageFile.info`.
* `thumbnails` - list of `HeifThumbnail` objects.

### The HeifThumbnail object

* `size` - the size of the image as a `(width, height)` tuple of integers.
* `has_alpha` - is a boolean indicating the presence of an alpha channel.
* `mode` - the image mode, e.g. 'RGB' or 'RGBA'.
* `bit_depth` - the number of bits in each component of a pixel.
* `data` - the raw decoded file data, as bytes.
* `stride` - the number of bytes in a row of decoded file data.
* `img_index` - index of image for which this thumbnail is.
