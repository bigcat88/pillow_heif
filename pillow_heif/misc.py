"""
Different miscellaneous helper functions.

Mostly for internal use, so prototypes can change between versions.
"""

import builtins
import pathlib
from struct import pack, unpack
from typing import Union
from warnings import warn

from _pillow_heif_cffi import ffi, lib

try:
    from defusedxml import ElementTree
except ImportError:  # pragma: no cover
    ElementTree = None  # pragma: no cover


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
    Wrapper around `libheif.get_file_mimetype`

    :param fp: A filename (string), pathlib.Path object, file object or bytes.
       The file object must implement ``file.read``, ``file.seek`` and ``file.tell`` methods,
       and be opened in binary mode.
    :returns: "image/heic", "image/heif", "image/heic-sequence",
        "image/heif-sequence", "image/avif" or "image/avif-sequence"
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


def getxmp(xmp_data) -> dict:
    """
    Returns a dictionary containing the XMP tags.
    Requires defusedxml to be installed.
    Copy of function `_getxmp` from Pillow.Image

    :returns: XMP tags in a dictionary.
    """

    def get_name(tag):
        return tag.split("}")[1]

    def get_value(element):
        value = {get_name(k): v for k, v in element.attrib.items()}
        children = list(element)
        if children:
            for child in children:
                name = get_name(child.tag)
                child_value = get_value(child)
                if name in value:
                    if not isinstance(value[name], list):
                        value[name] = [value[name]]
                    value[name].append(child_value)
                else:
                    value[name] = child_value
        elif value:
            if element.text:
                value["text"] = element.text
        else:
            return element.text
        return value

    if xmp_data:
        if ElementTree is None:
            warn("XMP data cannot be read without defusedxml dependency")
            return {}
        _clear_data = xmp_data.rsplit(b"\x00", 1)
        if _clear_data[0]:
            root = ElementTree.fromstring(_clear_data[0])
            return {get_name(root.tag): get_value(root)}
    return {}
