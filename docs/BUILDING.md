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
   * On Alpine need install `aom-dev`.
   * On Ubuntu(22.04+) you need install `libaom-dev`.
   * On Ubuntu less 22.04 you can compile it from source, but `AV1` codecs will be not available.
   * Encoder will not be available if you did not install `x265`. It is not build from source by default on armv7.

### MacOS
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install x265 libjpeg libde265 libheif
pip3 install --no-binary pillow_heif
```

### Windows
By default, build script assumes that `vcpkg` builds libs in `C:\vcpkg\installed\x64-windows`.
If not, then set `VCPKG_PREFIX` environment variable to your custom path, e.g. `setx VCPKG_PREFIX "D:\vcpkg\installed\x64-windows"`
```bat
vcpkg install aom libheif --triplet=x64-windows
pip3 install --no-binary pillow_heif
```

Note: there is no support for 10/12 bit file formats for encoder now on Windows.
