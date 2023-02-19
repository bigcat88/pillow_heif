"""
Functions to get versions of underlying libraries.
"""

from _pillow_heif import lib_info


def libheif_version() -> str:
    """Returns ``libheif`` version."""

    return lib_info["libheif"]


def libheif_info() -> dict:
    """Returns a dictionary with version information.
    The keys `libheif`, `HEIF`, `AVIF` are always present, but values for `HEIF`/`AVIF` can be empty.

    {'libheif': '1.14.2',
     'HEIF': 'x265 HEVC encoder (3.4+31-6722fce1f)',
     'AVIF': 'AOMedia Project AV1 Encoder 3.5.0'
    }"""

    return lib_info
