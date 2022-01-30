# pillow_heif

![static-analysis](https://github.com/bigcat88/pillow_heif/actions/workflows/static-analysis.yml/badge.svg)
![build](https://github.com/bigcat88/pillow_heif/actions/workflows/create-release-draft.yml/badge.svg)
![published](https://github.com/bigcat88/pillow_heif/actions/workflows/publish-pypi.yaml/badge.svg)
![PythonVersion](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)
![pypi](https://img.shields.io/pypi/v/pillow_heif.svg)
[![Downloads](https://static.pepy.tech/personalized-badge/pillow-heif?period=month&units=international_system&left_color=grey&right_color=orange&left_text=Downloads/Month)](https://pepy.tech/project/pillow-heif)


A HEIF/HEIC add-on for Pillow using the `libheif` library via `CFFI`, with binary wheels (Python 3.6-3.9, linux/macos - x64, aarch64).

Mostly based on David Poirier's [pyheif](https://github.com/carsales/pyheif).
The idea for this plugin came from Christian Bianciotto's [pyheif-pillow-opener](https://github.com/ciotto/pyheif-pillow-opener).
Many thanks!

Pull requests are greatly welcome.

## Installation
You can install pillow_heif from [PyPi](https://pypi.org/project/pillow-heif/):

```pip install pillow_heif```

or from [GitHub](https://github.com/bigcat88/pillow_heif):

```pip install https://github.com/bigcat88/pillow_heif/archive/master.zip```

## Installation from source

##### Linux Ubuntu
```
sudo add-apt-repository ppa:strukturag/libheif
apt install libffi libheif-dev libde265-dev
pip install git+https://github.com/bigcat88/pillow_heif.git
```

##### MacOS
```
brew install libffi libheif
pip3 install git+https://github.com/bigcat88/pillow_heif.git
```
If on MacOs it fails with installing from source, just try second time(helps me on M1 with Monerey):
```
pip3 install git+https://github.com/bigcat88/pillow_heif.git
```

##### Windows
With Visual Studio 2015+ C Compiler and SDK installed:
```
set INCLUDE=%INCLUDE%;X:\path\to\libheif\source
set LIB=%LIB%;X:\path\to\libheif\build
pip install git+https://github.com/bigcat88/pillow_heif.git
```

## Example of use as opener
```
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

image = Image.open('image.heic')
image.load()
```

## Example of use as reader

```
from PIL import Image
import pillow_heif

heif_file = pillow_heif.read("ABC.HEIC")
image = Image.frombytes(
    heif_file.mode, 
    heif_file.size, 
    heif_file.data,
    "raw",
    heif_file.mode,
    heif_file.stride,
    )
```

### The HeifFile object

The returned `HeifFile` has the following properties:

* `size` - the size of the image as a `(width, height)` tuple of integers
* `brand` - a list of heif_brand constants
* `has_alpha`  - (bool)presence of alpha channel
* `mode` - the image mode, e.g. "RGB" or "RGBA"
* `bit_depth` - the number of bits in each component of a pixel
* `metadata` - a list of metadata dictionaries
* `color_profile` - a color profile dictionary
* `data` - the raw decoded file data, as bytes
* `stride` - the number of bytes in a row of decoded file data
