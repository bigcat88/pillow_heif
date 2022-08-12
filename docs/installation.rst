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
        and in ``docker`` folder there are docker files for ``Ubuntu`` and ``Alpine`` with examples how to build
        from source.

There is many different ways how to build it from source. Main requirements are:
    * libheif should be version ``1.12``
    * ``x265`` should support 10 - 12 bit encoding(if you want to save in that bitness)
    * ``aom`` should be >= ``3.0.0`` version

``Ubuntu 22.04`` have all that in their repositories, so you can just install ``libehif`` with:

| :bash:`sudo apt install -y libaom-dev libx265-dev libde265-dev libheif-dev`

and after that compile it from source.

If you have questions about custom build from sources you can ask them in discussions or create an issue.
And for those who needs only ``HEIF`` decoding, there is a github action file `build-ph-lite` that builds wheels only with
``libde265`` and ``libheif``.

Also if you are Guru in ``cmake`` and ``c++`` and find any error, I'll be glad for any pull requests.

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

`GA Action to test building from source <https://github.com/bigcat88/pillow_heif/blob/master/.github/workflows/test-src-build-windows.yml>`_.

.. note::
    | On Windows installation is a bit tricky...
    | First install `msys2 <https://www.msys2.org/>`_, if it is not installed.
    | By default, build script assumes that **msys2** builds libs in :bash:`C:\msys64\mingw64`
    | You can set **MSYS2_PREFIX** environment variable to your custom path, e.g.:
    | :bash:`setx MSYS2_PREFIX "D:\msys64\mingw64"`

Using **msys2** terminal change working directory and install `libheif`::

    cd .../pillow_heif/libheif/windows/mingw-w64-libheif
    makepkg-mingw --syncdeps
    pacman -U mingw-w64-x86_64-libheif-1.12.0-9-any.pkg.tar.zst

.. note::
    This is needed, so we dont want to `dav1d` or `rav1e` to be installed as the dependencies.

Now install Pillow-Heif with something like this::

    python -m pip install --upgrade pillow-heif --no-binary :all:

| After that copy **libheif.dll**, **libaom.dll**, **libde265-0.dll**, **libx265.dll**,
    **libgcc_s_seh-1.dll**, **libstdc++-6.dll** and **libwinpthread-1.dll** from
    *msys64\\mingw6\\bin* to python site-packages root.
