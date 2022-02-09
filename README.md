# pillow_heif

![static-analysis](https://github.com/bigcat88/pillow_heif/actions/workflows/static-analysis.yml/badge.svg)
![build](https://github.com/bigcat88/pillow_heif/actions/workflows/create-release-draft.yml/badge.svg)
![published](https://github.com/bigcat88/pillow_heif/actions/workflows/publish-pypi.yaml/badge.svg)
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

A HEIF/HEIC add-on for Pillow using the `libheif` library via `CFFI`.

Binary wheels for Python 3.6-3.10. Linux(+Alpine)/macOS/Windows - x64/aarch64.

#### **_Version 0.1.6 was last to support Python 3.6._**

Mostly based on David Poirier's [pyheif](https://github.com/carsales/pyheif).
The idea for this plugin came from Christian Bianciotto's [pyheif-pillow-opener](https://github.com/ciotto/pyheif-pillow-opener).
Many thanks!

Pull requests are greatly welcome.

## Installation
(Recommended) You can install pillow_heif from [PyPi](https://pypi.org/project/pillow-heif/):

```pip install pillow_heif```


## Installation from source
**(NOT RECOMMENDED)**

##### Linux Ubuntu
```
sudo add-apt-repository ppa:strukturag/libheif
apt install libffi libheif-dev libde265-dev
pip install git+https://github.com/bigcat88/pillow_heif.git
```

##### MacOS
```
brew install x265 libjpeg libde265 libheif
pip3 install git+https://github.com/bigcat88/pillow_heif.git
```

##### Windows
With vcpkg and Visual Studio 2015+ Tools installed:
```
vcpkg install aom libheif --triplet=x64-windows
VCPKG_PREFIX="path_to:vcpkg/installed/x64-windows"
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

heif_file = pillow_heif.read('ABC.HEIC')
image = Image.frombytes(
    heif_file.mode,
    heif_file.size,
    heif_file.data,
    'raw',
    heif_file.mode,
    heif_file.stride,
    )
```

### The HeifFile object

The returned `HeifFile` has the following properties:

* `size` - the size of the image as a `(width, height)` tuple of integers
* `brand` - a list of heif_brand constants
* `has_alpha`  - (bool)presence of alpha channel
* `mode` - the image mode, e.g. 'RGB' or 'RGBA'
* `bit_depth` - the number of bits in each component of a pixel
* `metadata` - a list of metadata dictionaries
* `color_profile` - a color profile dictionary
* `data` - the raw decoded file data, as bytes
* `stride` - the number of bytes in a row of decoded file data
