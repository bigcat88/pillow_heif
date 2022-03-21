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
Here is a GH Action [Dockerfile](https://github.com/bigcat88/pillow_heif/blob/master/docker/from_src.Dockerfile) for test building from source.

Notes:

1. Building for first time will take a long time, if in your system `cmake` version `>=3.16.1` is not present.
2. Arm7(32 bit):
   * On Alpine you need install `aom-dev`.
   * On Ubuntu(22.04+) you need install `libaom-dev`.
   * On Ubuntu less then 22.04 you can compile it from source, but `AV1` codecs will be not avalaible.

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
