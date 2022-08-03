Installation
============

Basic Installation
------------------

.. note::

    This is a recommended way of installation for use.

Install Pillow-Heif with :command:`pip`::

    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade pillow-heif


Wheels are present for all systems supported by `cibuildwheel <https://cibuildwheel.readthedocs.io/en/stable/>`_

Building From Source
--------------------

    All **pillow-heif's** **PyPi** packages are build on GitHub Actions, so you can take a look at `it <https://github.com/bigcat88/pillow_heif/blob/master/.github/workflows/create-release-draft.yml>`_.

.. role:: bash(code)
   :language: bash

Linux
^^^^^

.. note::

    | For installing external libraries, you should run install with **root** privileges.
    | See `build_libs.py <https://github.com/bigcat88/pillow_heif/blob/master/libheif/build_libs.py>`_ for
        additional info what will happen during installing from source...
    | Here is a
        `GH Action <https://github.com/bigcat88/pillow_heif/blob/master/.github/workflows/test-src-build.yml>`_
        and a `Dockerfile <https://github.com/bigcat88/pillow_heif/blob/master/docker/from_src.Dockerfile>`_
        for test building from source.

Debian based
""""""""""""

| :bash:`sudo apt install -y python3-pip libffi-dev libtool git cmake g++`
| :bash:`sudo -H python3 -m pip install --upgrade pip`
| :bash:`sudo -H python3 -m pip install --upgrade pillow-heif --no-binary :all:`

For relatively fresh Linuxes like ``Ubuntu 22.04`` you can install:

| :bash:`sudo apt install -y libaom-dev libx265-dev libde265-dev libheif-dev`

and after that build `pillow-heif` in a minute.

Alpine based
""""""""""""

| :bash:`sudo apk --no-cache add py3-pip python3-dev libtool git gcc m4 perl alpine-sdk cmake`
| :bash:`sudo apk --no-cache add fribidi-dev harfbuzz-dev jpeg-dev lcms2-dev openjpeg-dev`
| :bash:`sudo -H python3 -m pip install --upgrade pip`
| :bash:`sudo -H python3 -m pip install --upgrade pillow-heif --no-binary :all:`

macOS
^^^^^

First install `Homebrew <https://brew.sh>`_, if it is not installed and run::

    brew install x265 libjpeg libde265 libheif
    python3 -m pip install --upgrade pip

Now install Pillow-Heif with::

    python3 -m pip install --upgrade pillow-heif --no-binary :all:

or from within the uncompressed source directory::

    python3 -m pip install .

Windows
^^^^^^^

.. note::
    | On Windows installation is a bit tricky...
    | First install `msys2 <https://www.msys2.org/>`_, if it is not installed.
    | By default, build script assumes that **msys2** builds libs in :bash:`C:\msys64\mingw64`
    | You can set **VCPKG_PREFIX** environment variable to your custom path, e.g.:
    | :bash:`setx VCPKG_PREFIX "D:\msys64\mingw64"`

Using **msys2** terminal change working directory and install `libheif`::

    cd .../pillow_heif/libheif/mingw-w64-libheif
    makepkg-mingw --syncdeps
    pacman -U mingw-w64-x86_64-libheif-1.12.0-9-any.pkg.tar.zst

.. note::
    This is needed, so we dont want to `dav1d` or `rav1e` to be installed as dependencies.

Now install Pillow-Heif with::

    python3 -m pip install --upgrade pillow-heif --no-binary :all:

| After that copy **libheif.dll**, **libaom.dll**, **libde265.dll** and **libx265.dll** from
    *msys64\\mingw6\\bin* to site-packages root or simply add **...\\msys2\\mingw64\\bin** to dll load path.
