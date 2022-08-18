# pi-heif

![Mac OS](https://img.shields.io/badge/mac%20os-FCC624?style=for-the-badge&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-0078D6.svg?style=for-the-badge&logo=alpine-linux&logoColor=white)

This is a light version of [Pillow-Heif](https://github.com/bigcat88/pillow_heif) with more permissive license for wheels.

Usage and all codebase are the same, refer to [pillow-heif docs](https://readthedocs.org/projects/pillow-heif/badge/?version=latest)

### Install
```console
python3 -m pip install -U pip
python3 -m pip install pi-heif
```

### Example of use as a Pillow plugin
```python3
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

im = Image.open("images/input.heic")  # do whatever need with a Pillow image
im.show()
```

### Wheels

| **_Wheels table_** | macOS<br/>Intel | macOS<br/>Silicon | Windows<br/>64bit | musllinux* | manylinux* |
|--------------------|:---------------:|:-----------------:|:-----------------:|:----------:|:----------:|
| CPython 3.6        |       N/A       |        N/A        |        N/A        |     ✅      |     ✅      |
| CPython 3.7        |        ✅        |        N/A        |         ✅         |     ✅      |     ✅      |
| CPython 3.8        |        ✅        |         ✅         |         ✅         |     ✅      |     ✅      |
| CPython 3.9        |        ✅        |         ✅         |         ✅         |     ✅      |     ✅      |
| CPython 3.10       |        ✅        |         ✅         |         ✅         |     ✅      |     ✅      |
| CPython 3.11       |        ✅        |         ✅         |         ✅         |     ✅      |     ✅      |
| PyPy 3.7 v7.3      |        ✅        |        N/A        |        N/A        |    N/A     |     ✅      |
| PyPy 3.8 v7.3      |        ✅        |        N/A        |        N/A        |    N/A     |     ✅      |

&ast; **i686**, **x86_64**, **aarch64** wheels.
