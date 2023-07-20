"""
Different miscellaneous helper functions.

Mostly for internal use, so prototypes can change between versions.
"""

import builtins
import re
from dataclasses import dataclass
from enum import IntEnum
from math import ceil
from pathlib import Path
from struct import pack, unpack
from typing import List, Optional

from PIL import Image
from PIL import __version__ as pil_version

from . import options
from .constants import HeifChroma, HeifColorspace, HeifCompressionFormat

try:
    import _pillow_heif
except ImportError as ex:
    from ._deffered_error import DeferredError

    _pillow_heif = DeferredError(ex)


MODE_INFO = {
    # name -> [channels, bits per pixel channel, colorspace, chroma]
    "BGRA;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "BGRa;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "BGR;16": (3, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE),
    "RGBA;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "RGBa;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "RGB;16": (3, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE),
    "LA;16": (2, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "La;16": (2, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "L;16": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "I;16": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "I;16L": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "BGRA;12": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "BGRa;12": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "BGR;12": (3, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE),
    "RGBA;12": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "RGBa;12": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "RGB;12": (3, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE),
    "LA;12": (2, 12, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "La;12": (2, 12, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "L;12": (1, 12, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "I;12": (1, 12, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "I;12L": (1, 12, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "BGRA;10": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "BGRa;10": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "BGR;10": (3, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE),
    "RGBA;10": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "RGBa;10": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE),
    "RGB;10": (3, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE),
    "LA;10": (2, 10, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "La;10": (2, 10, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "L;10": (1, 10, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "I;10": (1, 10, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "I;10L": (1, 10, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "RGBA": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA),
    "RGBa": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA),
    "RGB": (3, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGB),
    "BGRA": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA),
    "BGRa": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA),
    "BGR": (3, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGB),
    "LA": (2, 8, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "La": (2, 8, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
    "L": (1, 8, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME),
}


def set_orientation(info: dict) -> Optional[int]:
    """Reset orientation in ``EXIF`` to ``1`` if any orientation present.
    Removes ``XMP`` orientation tag if it is present.
    In Pillow plugin mode it called automatically for images.
    When ``pillow_heif`` used in ``standalone`` mode, if you wish you can call it manually.

    .. note:: If there is no orientation tag, this function will not add it and do nothing.

        If both XMP and EXIF orientation tags present, EXIF orientation tag will be returned,
        but both tags will be removed.

    :param info: `info` dictionary from :external:py:class:`~PIL.Image.Image` or :py:class:`~pillow_heif.HeifImage`.
    :returns: Original orientation or None if it is absent."""

    original_orientation = None
    if info.get("exif", None):
        try:
            tif_tag = info["exif"]
            skipped_exif00 = False
            if tif_tag.startswith(b"Exif\x00\x00"):
                skipped_exif00 = True
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
                    p_value = pointer + 8
                    if skipped_exif00:
                        p_value += 6
                    new_orientation = pack(endian_mark + "H", 1)
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
    if isinstance(fp, (str, Path)):
        with builtins.open(fp, "rb") as file:
            return file.read(length or -1)
    if hasattr(fp, "read"):
        offset = fp.tell() if hasattr(fp, "tell") else None
        result = fp.read(length or -1)
        if offset is not None and hasattr(fp, "seek"):
            fp.seek(offset)
        return result
    return bytes(fp)[:length]


def _retrieve_exif(metadata: List[dict]) -> Optional[bytes]:
    _result = None
    _purge = []
    for i, md_block in enumerate(metadata):
        if md_block["type"] == "Exif":
            _purge.append(i)
            skip_size = int.from_bytes(md_block["data"][:4], byteorder="big", signed=False)
            skip_size += 4  # skip 4 bytes with offset
            if len(md_block["data"]) - skip_size <= 4:  # bad EXIF data, skip first 4 bytes
                skip_size = 4
            elif skip_size >= 6:
                if md_block["data"][skip_size - 6 : skip_size] == b"Exif\x00\x00":
                    skip_size -= 6
            _data = md_block["data"][skip_size:]
            if not _result and _data:
                _result = _data
    for i in reversed(_purge):
        del metadata[i]
    return _result


def _retrieve_xmp(metadata: List[dict]) -> Optional[bytes]:
    _result = None
    _purge = []
    for i, md_block in enumerate(metadata):
        if md_block["type"] == "mime":
            _purge.append(i)
            if not _result:
                _result = md_block["data"]
    for i in reversed(_purge):
        del metadata[i]
    return _result


def _exif_from_pillow(img: Image.Image) -> Optional[bytes]:
    if "exif" in img.info:
        return img.info["exif"]
    if hasattr(img, "getexif"):
        if pil_version[:4] not in ("9.1.",):
            exif = img.getexif()
            if exif:
                return exif.tobytes()
    return None


def _xmp_from_pillow(img: Image.Image) -> Optional[bytes]:
    _xmp = None
    if "xmp" in img.info:
        _xmp = img.info["xmp"]
    elif "XML:com.adobe.xmp" in img.info:  # PNG
        _xmp = img.info["XML:com.adobe.xmp"]
    elif hasattr(img, "tag_v2"):  # TIFF
        if 700 in img.tag_v2:
            _xmp = img.tag_v2[700]
    elif hasattr(img, "applist"):  # JPEG
        for segment, content in img.applist:
            if segment == "APP1":
                marker, xmp_tags = content.rsplit(b"\x00", 1)
                if marker == b"http://ns.adobe.com/xap/1.0/":
                    _xmp = xmp_tags
                    break
    if isinstance(_xmp, str):
        _xmp = _xmp.encode("utf-8")
    return _xmp


def _pil_to_supported_mode(img: Image.Image) -> Image.Image:
    if img.mode == "P":
        mode = "RGBA" if img.info.get("transparency") else "RGB"
        img = img.convert(mode=mode)
    elif img.mode == "I":
        img = img.convert(mode="I;16L")
    elif img.mode == "1":
        img = img.convert(mode="L")
    elif img.mode == "CMYK":
        img = img.convert(mode="RGBA")
    elif img.mode == "YCbCr":  # note: libheif supports native `YCbCr`.
        img = img.convert(mode="RGB")
    return img


class Transpose(IntEnum):
    # Temporary till we support old Pillows, remove this when minimum Pillow version will have this.
    FLIP_LEFT_RIGHT = 0
    FLIP_TOP_BOTTOM = 1
    ROTATE_90 = 2
    ROTATE_180 = 3
    ROTATE_270 = 4
    TRANSPOSE = 5
    TRANSVERSE = 6


def _rotate_pil(img: Image.Image, orientation: int) -> Image.Image:
    # Probably need create issue in Pillow to add support
    # for info["xmp"] or `getxmp()` for ImageOps.exif_transpose and remove this func.
    method = {
        2: Transpose.FLIP_LEFT_RIGHT,
        3: Transpose.ROTATE_180,
        4: Transpose.FLIP_TOP_BOTTOM,
        5: Transpose.TRANSPOSE,
        6: Transpose.ROTATE_270,
        7: Transpose.TRANSVERSE,
        8: Transpose.ROTATE_90,
    }.get(orientation)
    if method is not None:
        return img.transpose(method)
    return img


def _get_primary_index(some_iterator, primary_index: Optional[int]) -> int:
    primary_attrs = [_.info.get("primary", False) for _ in some_iterator]
    if primary_index is None:
        primary_index = 0
        for i, v in enumerate(primary_attrs):
            if v:
                primary_index = i
    elif primary_index == -1 or primary_index >= len(primary_attrs):
        primary_index = len(primary_attrs) - 1
    return primary_index


class CtxEncode:
    def __init__(self, compression_format: HeifCompressionFormat, **kwargs):
        quality = kwargs.get("quality", options.QUALITY)
        self.ctx_write = _pillow_heif.CtxWrite(compression_format, -2 if quality is None else quality)
        enc_params = kwargs.get("enc_params", {})
        chroma = kwargs.get("chroma", None)
        if chroma:
            enc_params["chroma"] = chroma
        for key, value in enc_params.items():
            _value = value if isinstance(value, str) else str(value)
            self.ctx_write.set_parameter(key, _value)

    def add_image(self, size: tuple, mode: str, data, **kwargs) -> None:
        if size[0] <= 0 or size[1] <= 0:
            raise ValueError("Empty images are not supported.")
        bit_depth_in = MODE_INFO[mode][1]
        bit_depth_out = 8 if bit_depth_in == 8 else kwargs.get("bit_depth", 16)
        if bit_depth_out == 16:
            bit_depth_out = 12 if options.SAVE_HDR_TO_12_BIT else 10
        premultiplied_alpha = int(mode.split(sep=";")[0][-1] == "a")
        # creating image
        im_out = self.ctx_write.create_image(size, MODE_INFO[mode][2], MODE_INFO[mode][3], premultiplied_alpha)
        # image data
        if MODE_INFO[mode][0] == 1:
            im_out.add_plane_l(size, bit_depth_out, bit_depth_in, data, kwargs.get("stride", 0))
        elif MODE_INFO[mode][0] == 2:
            im_out.add_plane_la(size, bit_depth_out, bit_depth_in, data, kwargs.get("stride", 0))
        else:
            im_out.add_plane(size, bit_depth_out, bit_depth_in, data, mode.find("BGR") != -1, kwargs.get("stride", 0))
        # color profile
        __icc_profile = kwargs.get("icc_profile", None)
        if __icc_profile is not None:
            im_out.set_icc_profile(kwargs.get("icc_profile_type", "prof"), __icc_profile)
        elif kwargs.get("nclx_profile", None):
            nclx_profile = kwargs["nclx_profile"]
            im_out.set_nclx_profile(
                *[
                    nclx_profile[i]
                    for i in ("color_primaries", "transfer_characteristics", "matrix_coefficients", "full_range_flag")
                ]
            )
        # encode
        im_out.encode(
            self.ctx_write, kwargs.get("primary", False), kwargs.get("save_nclx_profile", options.SAVE_NCLX_PROFILE)
        )
        # adding metadata
        exif = kwargs.get("exif", None)
        if exif is not None:
            if isinstance(exif, Image.Exif):
                exif = exif.tobytes()
            im_out.set_exif(self.ctx_write, exif)
        xmp = kwargs.get("xmp", None)
        if xmp is not None:
            im_out.set_xmp(self.ctx_write, xmp)
        for metadata in kwargs.get("metadata", []):
            im_out.set_metadata(self.ctx_write, metadata["type"], metadata["content_type"], metadata["data"])
        # adding thumbnails
        for thumb_box in kwargs.get("thumbnails", []):
            if max(size) > thumb_box > 3:
                im_out.encode_thumbnail(self.ctx_write, thumb_box)

    def save(self, fp) -> None:
        data = self.ctx_write.finalize()
        if isinstance(fp, (str, Path)):
            with builtins.open(fp, "wb") as f:
                f.write(data)
        elif hasattr(fp, "write"):
            fp.write(data)
        else:
            raise TypeError("`fp` must be a path to file or an object with `write` method.")


@dataclass
class MimCImage:
    def __init__(self, mode: str, size: tuple, data: bytes, **kwargs):
        self.mode = mode
        self.size = size
        self.stride: int = kwargs.get("stride", size[0] * MODE_INFO[mode][0] * ceil(MODE_INFO[mode][1] / 8))
        self.data = data
        self.metadata: List[dict] = []
        self.color_profile = None
        self.thumbnails: List[int] = []
        self.depth_image_list: List = []
        self.primary = False

    @property
    def size_mode(self):
        return self.size, self.mode

    @property
    def bit_depth(self):
        return MODE_INFO[self.mode][1]
