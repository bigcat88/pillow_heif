# pillow_heif

![static-analysis](https://github.com/bigcat88/pillow_heif/actions/workflows/analysis-coverage.yml/badge.svg)
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

A HEIF/HEIC/AVIF add-on for Pillow using the `libheif` library via `CFFI`.

Binary wheels for Python 3.6-3.10. Linux(+Alpine)/macOS/Windows - i686, x86_64 and aarch64.

#### **_Version 0.1.9 will be last to support Python 3.6._**

Mostly based on David Poirier's [pyheif](https://github.com/carsales/pyheif).
The idea for this plugin came from Christian Bianciotto's [pyheif-pillow-opener](https://github.com/ciotto/pyheif-pillow-opener).
Many thanks!

Pull requests are greatly welcome.

## Installation
(Recommended) From [PyPi](https://pypi.org/project/pillow-heif/):

```bash
pip3 install pillow_heif
```


## Installation from source
_Instructions are valid for version 0.1.7+_

### Linux

#### Debian(Ubuntu):
```bash
sudo apt install -y python3-pip libtool git
sudo -H python3 -m pip install --upgrade pip
sudo -H python3 -m pip install --no-binary pillow_heif
```


#### Alpine:
```bash
sudo apk --no-cache add py3-pip python3-dev libtool git gcc m4 perl alpine-sdk
sudo apk --no-cache add freetype-dev fribidi-dev harfbuzz-dev jpeg-dev lcms2-dev openjpeg-dev tiff-dev zlib-dev
sudo -H python3 -m pip install --upgrade pip
sudo -H python3 -m pip install --no-binary pillow_heif
```

See [build_libs_linux](https://github.com/bigcat88/pillow_heif/blob/master/libheif/build_libs.py) for additional info what will happen during installing from source.

Note: building for first time will take a long time, if in your system `cmake` version `>=3.22.1` is not present.


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
