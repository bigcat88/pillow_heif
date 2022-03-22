"""
Different miscellaneous helper functions.

Mostly for internal use, so prototypes can change between versions.
"""

from struct import pack, unpack
from typing import Union


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
