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

.. role:: bash(code)
   :language: bash

Linux
^^^^^

.. note::

    | For installing external libraries, you should run install with **root** rights.
    | See `build_libs.py <https://github.com/bigcat88/pillow_heif/blob/master/libheif/build_libs.py>`_ for
        additional info what will happen during installing from source...
    | Here is a
        `GH Action <https://github.com/bigcat88/pillow_heif/blob/master/.github/workflows/test-src-build.yml>`_
        and a `Dockerfile <https://github.com/bigcat88/pillow_heif/blob/master/docker/from_src.Dockerfile>`_
        for test building from source.

Debian based
""""""""""""

| :bash:`sudo apt install -y python3-pip libtool git cmake`
| :bash:`sudo -H python3 -m pip install --upgrade pip`
| :bash:`sudo -H python3 -m pip install --upgrade pillow-heif --no-binary :all:`

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
    | First install `vcpkg <https://vcpkg.io/en/getting-started.html>`_, if it is not installed.
    | By default, build script assumes that **vcpkg** builds libs in *C:\\vcpkg\\installed\\x64-windows*
    | You can set **VCPKG_PREFIX** environment variable to your custom path, e.g.:
    | :bash:`setx VCPKG_PREFIX "D:\vcpkg\installed\x64-windows"`

Using **vcpkg** install required libraries::

    vcpkg install aom libheif --triplet=x64-windows

Now install Pillow-Heif with::

    python3 -m pip install --upgrade pillow-heif --no-binary :all:

| After that copy **heif.dll**, **aom.dll**, **libde265.dll** and **libx265.dll** from
    *vcpkg\\installed\\x64-windows\\bin* to site-packages root.
