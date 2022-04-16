"""
Different miscellaneous helper functions.

Mostly for internal use, so prototypes can change between versions.
"""

import builtins
import pathlib
from struct import pack, unpack
from typing import Union

from _pillow_heif_cffi import ffi, lib

from .constants import HeifChroma


def reset_orientation(info: dict) -> Union[int, None]:
    """
    Sets `orientation` in `exif` to `1` if any presents. In Pillow plugin mode it called automatically for main image.
    When `pillow_heif` used as a reader, if you wish you can call it manually.

    :param info: An `info` dictionary from `ImageFile.ImageFile` or `UndecodedHeifImage`.
    :returns: Original orientation or None if it is absent.
    """
    if info.get("exif", None):
        tif_tag = info["exif"][6:]
        endian_mark = "<" if tif_tag[0:2] == b"\x49\x49" else ">"
        pointer = unpack(endian_mark + "L", tif_tag[4:8])[0]
        tag_count = unpack(endian_mark + "H", tif_tag[pointer : pointer + 2])[0]
        offset = pointer + 2
        for tag_n in range(tag_count):
            pointer = offset + 12 * tag_n
            if unpack(endian_mark + "H", tif_tag[pointer : pointer + 2])[0] != 274:
                continue
            value = tif_tag[pointer + 8 : pointer + 12]
            data = unpack(endian_mark + "H", value[0:2])[0]
            if data != 1:
                p_value = 6 + pointer + 8
                info["exif"] = info["exif"][:p_value] + pack(endian_mark + "H", 1) + info["exif"][p_value + 2 :]
            return data
    return None


def get_file_mimetype(fp) -> str:
    """
    Wrapper around `libheif.get_file_mimetype`.

    :param fp: A filename (string), pathlib.Path object, file object or bytes.
       The file object must implement ``file.read``, ``file.seek`` and ``file.tell`` methods,
       and be opened in binary mode.
    :returns: string with `image/*`. If the format could not be detected, an empty string is returned.
    """
    __data = _get_bytes(fp, 50)
    return ffi.string(lib.heif_get_file_mime_type(__data, len(__data))).decode()


def _get_bytes(fp, length=None) -> bytes:
    if isinstance(fp, (str, pathlib.Path)):
        with builtins.open(fp, "rb") as file:
            return file.read(length or -1)
    if hasattr(fp, "read"):
        offset = fp.tell() if hasattr(fp, "tell") else None
        result = fp.read(length or -1)
        if offset is not None and hasattr(fp, "seek"):
            fp.seek(offset)
        return result
    return bytes(fp)[:length]


def _get_chroma(bit_depth: int, has_alpha: bool, hdr_to_8bit: bool = False) -> HeifChroma:
    if hdr_to_8bit or bit_depth <= 8:
        chroma = HeifChroma.INTERLEAVED_RGBA if has_alpha else HeifChroma.INTERLEAVED_RGB
    else:
        if has_alpha:
            chroma = HeifChroma.INTERLEAVED_RRGGBBAA_BE
        else:
            chroma = HeifChroma.INTERLEAVED_RRGGBB_BE
    return chroma
