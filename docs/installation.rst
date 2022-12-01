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

    All **pillow-heif's** **PyPi** packages are build on GitHub Actions, so you can take a look at `it <https://github.com/bigcat88/pillow_heif/blob/master/.github/workflows/publish-pypi.yml>`_.

.. role:: bash(code)
   :language: bash

Linux
^^^^^

.. note::

    | For installing external libraries(if they are not present in system), you should run install with **root** privileges.
    | See `build_libs.py <https://github.com/bigcat88/pillow_heif/blob/master/libheif/linux_build_libs.py>`_ for
        additional info what will happen during installing from source...
    | Here is a
        `GH Action <https://github.com/bigcat88/pillow_heif/blob/master/.github/workflows/test-src-build-linux.yml>`_
        and in ``docker/from_src`` folder there are docker files for ``Debian``, ``Ubuntu`` and ``Alpine`` with examples
        how to build from source.

There is many different ways how to build it from source. Main requirements are:
    * libheif should be version ``1.13``, ``1.14`` or ``1.14.1``
    * ``x265`` should support 10 - 12 bit encoding(if you want to save in that bitness)
    * ``aom`` should be >= ``3.3.0`` version
    * ``libde265`` should be >= ``1.0.8`` version

``Ubuntu 22.04`` have all that in their repositories, except ``libheif`` (it has only ``1.12.0`` version):

| :bash:`sudo apt install -y libaom-dev libx265-dev libde265-dev`

and after that you should build libheif yourself(or run pip install with `root` privileges).

.. note:: Alpine ``3.17`` has libheif ``1.14.0`` version in their repositories.

If you have questions about custom build from sources you can ask them in discussions or create an issue.

macOS
^^^^^

`GA Action to test build on macOS from source <https://github.com/bigcat88/pillow_heif/blob/master/.github/workflows/test-src-build-macos.yml>`_

First install `Homebrew <https://brew.sh>`_, if it is not installed and run::

    brew install x265 libjpeg libde265 libheif
    python3 -m pip install --upgrade pip

Now install Pillow-Heif with::

    python3 -m pip install --upgrade pillow-heif --no-binary :all:

or from within the uncompressed source directory::

    python3 -m pip install .

Windows
^^^^^^^

`GA Action to test build on Windows from source <https://github.com/bigcat88/pillow_heif/blob/master/.github/workflows/test-src-build-windows.yml>`_

.. note::
    | On Windows installation is a bit tricky...
    | First install `msys2 <https://www.msys2.org/>`_, if it is not installed.
    | By default, build script assumes that **msys2** builds libs in :bash:`C:/msys64/mingw64`
    | You can set **MSYS2_PREFIX** environment variable to your custom path, e.g.:
    | :bash:`setx MSYS2_PREFIX "D:/msys64/mingw64"`

Using **msys2** terminal change working directory and install `libheif`::

    cd .../pillow_heif/libheif/windows/mingw-w64-libheif
    makepkg-mingw --syncdeps
    pacman -U mingw-w64-x86_64-libheif-*-any.pkg.tar.zst

.. note::
    This is needed, so we dont want to `dav1d`, `rav1e` or `libSvtAv1Enc` to be installed as the dependencies.

Now inside Pillow-Heif directory install it with pip from source::

    python -m pip install .

| After that copy **libheif.dll**, **libaom.dll**, **libde265-0.dll**, **libx265.dll**,
    **libgcc_s_seh-1.dll**, **libstdc++-6.dll** and **libwinpthread-1.dll** from
    *msys64\\mingw6\\bin* to python site-packages root.
