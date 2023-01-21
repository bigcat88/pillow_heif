"""
Different miscellaneous helper functions.

Mostly for internal use, so prototypes can change between versions.
"""

import builtins
import pathlib
import re
from struct import pack, unpack
from typing import Union


def set_orientation(info: dict, orientation: int = 1) -> Union[int, None]:
    """Sets orientation in ``EXIF`` to ``1`` by default if any orientation present.
    Removes ``XMP`` orientation tag if it is present.
    In Pillow plugin mode it called automatically for images.
    When ``pillow_heif`` used in ``standalone`` mode, if you wish you can call it manually.

    .. note:: If there is no orientation tag, this function will not add it and do nothing.

        If both XMP and EXIF orientation tags present, EXIF orientation tag will be returned,
        but both tags will be removed.

    :param info: `info` dictionary from `~PIL.Image.Image` or `~pillow_heif.HeifImage`.
    :param orientation: int value of EXIF or XMP orientation tag.
    :returns: Original orientation or None if it is absent."""

    original_orientation = None
    if info.get("exif", None):
        try:
            tif_tag = info["exif"]
            if tif_tag.startswith(b"Exif\x00\x00"):
                tif_tag = tif_tag[6:]
            endian_mark = "<" if tif_tag[0:2] == b"\x49\x49" else ">"
            pointer = unpack(endian_mark + "L", tif_tag[4:8])[0]
            tag_count = unpack(endian_mark + "H", tif_tag[pointer : pointer + 2])[0]
            offset = pointer + 2
            for tag_n in range(tag_count):
                pointer = offset + 12 * tag_n
                if unpack(endian_mark + "H", tif_tag[pointer : pointer + 2])[0] != 274:
                    continue
                value = tif_tag[pointer + 8 : pointer + 12]
                _original_orientation = unpack(endian_mark + "H", value[0:2])[0]
                if _original_orientation != 1:
                    original_orientation = _original_orientation
                    p_value = 6 + pointer + 8
                    new_orientation = pack(endian_mark + "H", orientation)
                    info["exif"] = info["exif"][:p_value] + new_orientation + info["exif"][p_value + 2 :]
                    break
        except Exception:  # noqa # pylint: disable=broad-except
            pass
    if info.get("xmp", None):
        xmp_data = info["xmp"].rsplit(b"\x00", 1)
        if xmp_data[0]:
            decoded_xmp_data = None
            for encoding in ("utf-8", "latin1"):
                try:
                    decoded_xmp_data = xmp_data[0].decode(encoding)
                    break
                except Exception:  # noqa # pylint: disable=broad-except
                    pass
            if decoded_xmp_data:
                _original_orientation = 1
                match = re.search(r'tiff:Orientation(="|>)([0-9])', decoded_xmp_data)
                if match:
                    _original_orientation = int(match[2])
                    if original_orientation is None and _original_orientation != 1:
                        original_orientation = _original_orientation
                    decoded_xmp_data = re.sub(r'tiff:Orientation="([0-9])"', "", decoded_xmp_data)
                    decoded_xmp_data = re.sub(r"<tiff:Orientation>([0-9])</tiff:Orientation>", "", decoded_xmp_data)
                # should encode in "utf-8" anyway, as `defusedxml` do not work with `latin1` encoding.
                if encoding != "utf-8" or _original_orientation != 1:
                    info["xmp"] = b"".join([decoded_xmp_data.encode("utf-8"), b"\x00" if len(xmp_data) > 1 else b""])
    return original_orientation


def get_file_mimetype(fp) -> str:
    """Gets the MIME type of the HEIF(or AVIF) object.`

    :param fp: A filename (string), pathlib.Path object, file object or bytes.
        The file object must implement ``file.read``, ``file.seek`` and ``file.tell`` methods,
        and be opened in binary mode.
    :returns: "image/heic", "image/heif", "image/heic-sequence", "image/heif-sequence",
        "image/avif", "image/avif-sequence" or "".
    """

    heif_brand = _get_bytes(fp, 12)[8:]
    if heif_brand:
        if heif_brand == b"avif":
            return "image/avif"
        if heif_brand == b"avis":
            return "image/avif-sequence"
        if heif_brand in (b"heic", b"heix", b"heim", b"heis"):
            return "image/heic"
        if heif_brand in (b"hevc", b"hevx", b"hevm", b"hevs"):
            return "image/heic-sequence"
        if heif_brand == b"mif1":
            return "image/heif"
        if heif_brand == b"msf1":
            return "image/heif-sequence"
    return ""


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
