"""
Functions to get version of embedded C libraries.
"""


from _pillow_heif_cffi import ffi, lib


def libheif_version():
    return ffi.string(lib.heif_get_version()).decode()
