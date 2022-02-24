"""
Functions to get version of embedded C libraries.
"""


from _pillow_heif_cffi import ffi, lib  # pylint: disable=import-error, no-name-in-module


def libheif_version():
    return ffi.string(lib.heif_get_version()).decode()
