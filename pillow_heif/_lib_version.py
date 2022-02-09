"""
Functions to get version of embedded C libraries.
"""


from pillow_heif.libheif import ffi, lib  # pylint: disable=import-error, no-name-in-module


def libheif_version():
    return ffi.string(lib.heif_get_version()).decode()
