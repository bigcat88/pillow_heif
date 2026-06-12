"""Different miscellaneous helper functions.

Mostly for internal use, so prototypes can change between versions.
"""

import builtins
import re
from dataclasses import dataclass
from enum import IntEnum
from math import ceil
from pathlib import Path
from struct import pack, unpack

from PIL import Image

from . import options
from .constants import HeifChannel, HeifChroma, HeifColorspace, HeifCompressionFormat

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
    "YCbCr": (3, 8, HeifColorspace.YCBCR, HeifChroma.CHROMA_444),
}

SUBSAMPLING_CHROMA_MAP = {
    "4:4:4": 444,
    "4:2:2": 422,
    "4:2:0": 420,
}

LIBHEIF_CHROMA_MAP = {
    1: 420,
    2: 422,
    3: 444,
}


def save_colorspace_chroma(c_image, info: dict) -> None:
    """Converts `chroma` value from `c_image` to useful values and stores them in ``info`` dict."""
    # Saving of `colorspace` was removed, as currently is not clear where to use that value.
    chroma = LIBHEIF_CHROMA_MAP.get(c_image.chroma)
    if chroma is not None:
        info["chroma"] = chroma


def set_orientation(info: dict) -> int | None:
    """Reset orientation in ``EXIF`` to ``1`` if any orientation present.

    Removes ``XMP`` orientation tag if it is present.
    In Pillow plugin mode, it is called automatically for images.
    When ``pillow_heif`` used in ``standalone`` mode, if you wish, you can call it manually.

    .. note:: If there is no orientation tag, this function will not add it and do nothing.

        If both XMP and EXIF orientation tags are present, EXIF orientation tag will be returned,
        but both tags will be removed.

    :param info: `info` dictionary from :external:py:class:`~PIL.Image.Image` or :py:class:`~pillow_heif.HeifImage`.
    :returns: Original orientation or None if it is absent.
    """
    return _get_orientation(info, True)


def _get_orientation_for_encoder(info: dict) -> int:
    image_orientation = _get_orientation(info, False)
    return 1 if image_orientation is None else image_orientation


def _get_orientation_xmp(info: dict, exif_orientation: int | None, reset: bool = False) -> int | None:
    xmp_orientation = 1
    if info.get("xmp"):
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
                match = re.search(r'tiff:Orientation(="|>)([0-9])', decoded_xmp_data)
                if match:
                    xmp_orientation = int(match[2])
                    if reset:
                        decoded_xmp_data = re.sub(r'tiff:Orientation="([0-9])"', "", decoded_xmp_data)
                        decoded_xmp_data = re.sub(r"<tiff:Orientation>([0-9])</tiff:Orientation>", "", decoded_xmp_data)
                # should encode in "utf-8" anyway, as `defusedxml` do not work with `latin1` encoding.
                if encoding != "utf-8" or xmp_orientation != 1:
                    info["xmp"] = b"".join([decoded_xmp_data.encode("utf-8"), b"\x00" if len(xmp_data) > 1 else b""])
    return xmp_orientation if exif_orientation is None and xmp_orientation != 1 else None


def _get_orientation(info: dict, reset: bool = False) -> int | None:
    original_orientation = None
    if info.get("exif"):
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
                t_original_orientation = unpack(endian_mark + "H", value[0:2])[0]
                if t_original_orientation != 1:
                    original_orientation = t_original_orientation
                    if not reset:
                        break
                    p_value = pointer + 8
                    if skipped_exif00:
                        p_value += 6
                    new_orientation = pack(endian_mark + "H", 1)
                    info["exif"] = info["exif"][:p_value] + new_orientation + info["exif"][p_value + 2 :]
                    break
        except Exception:  # noqa # pylint: disable=broad-except
            pass
    xmp_orientation = _get_orientation_xmp(info, original_orientation, reset=reset)
    return xmp_orientation or original_orientation


def get_file_mimetype(fp) -> str:
    """Gets the MIME type of the HEIF(or AVIF) object.

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


def _retrieve_exif(metadata: list[dict]) -> bytes | None:
    result = None
    purge = []
    for i, md_block in enumerate(metadata):
        if md_block["type"] == "Exif":
            purge.append(i)
            skip_size = int.from_bytes(md_block["data"][:4], byteorder="big", signed=False)
            skip_size += 4  # skip 4 bytes with offset
            if len(md_block["data"]) - skip_size <= 4:  # bad EXIF data, skip first 4 bytes
                skip_size = 4
            elif skip_size >= 6 and md_block["data"][skip_size - 6 : skip_size] == b"Exif\x00\x00":
                skip_size -= 6
            data = md_block["data"][skip_size:]
            if not result and data:
                result = data
    for i in reversed(purge):
        del metadata[i]
    return result


def _retrieve_xmp(metadata: list[dict]) -> bytes | None:
    result = None
    purge = []
    for i, md_block in enumerate(metadata):
        if md_block["type"] == "mime":
            purge.append(i)
            if not result:
                result = md_block["data"]
    for i in reversed(purge):
        del metadata[i]
    return result


def _exif_from_pillow(img: Image.Image) -> bytes | None:
    if "exif" in img.info:
        return img.info["exif"]
    if hasattr(img, "getexif"):  # noqa
        exif = img.getexif()
        if exif:
            return exif.tobytes()
    return None


def _xmp_from_pillow(img: Image.Image) -> bytes | None:
    im_xmp = None
    if "xmp" in img.info:
        im_xmp = img.info["xmp"]
    elif "XML:com.adobe.xmp" in img.info:  # PNG
        im_xmp = img.info["XML:com.adobe.xmp"]
    if isinstance(im_xmp, str):
        im_xmp = im_xmp.encode("utf-8")
    return im_xmp


def _pil_to_supported_mode(img: Image.Image) -> Image.Image:
    # We support "YCbCr" for encoding in Pillow plugin mode and do not call this function.
    if img.mode == "P":
        mode = "RGBA" if img.info.get("transparency", None) is not None else "RGB"
        img = img.convert(mode=mode)
    elif img.mode == "I":
        img = img.convert(mode="I;16L")
    elif img.mode == "1":
        img = img.convert(mode="L")
    elif img.mode == "CMYK":
        img = img.convert(mode="RGBA")
    elif img.mode == "YCbCr":
        img = img.convert(mode="RGB")
    return img


class Transpose(IntEnum):
    """Temporary workaround till we support old Pillows, remove this when a minimum Pillow version will have this."""

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


def _get_primary_index(some_iterator, primary_index: int | None) -> int:
    primary_attrs = [_.info.get("primary", False) for _ in some_iterator]
    if primary_index is None:
        primary_index = 0
        for i, v in enumerate(primary_attrs):
            if v:
                primary_index = i
    elif primary_index == -1 or primary_index >= len(primary_attrs):
        primary_index = len(primary_attrs) - 1
    return primary_index


def __get_camera_intrinsic_matrix(values: tuple | None):
    return (
        {
            "focal_length_x": values[0],
            "focal_length_y": values[1],
            "principal_point_x": values[2],
            "principal_point_y": values[3],
            "skew": values[4],
        }
        if values
        else None
    )


def _get_heif_meta(c_image) -> dict:
    r = {}
    camera_intrinsic_matrix = __get_camera_intrinsic_matrix(c_image.camera_intrinsic_matrix)
    if camera_intrinsic_matrix:
        r["camera_intrinsic_matrix"] = camera_intrinsic_matrix
    camera_extrinsic_matrix_rot = c_image.camera_extrinsic_matrix_rot
    if camera_extrinsic_matrix_rot:
        r["camera_extrinsic_matrix_rot"] = camera_extrinsic_matrix_rot
    return r


def _extract_tile(
    data, src_stride: int, bytes_per_pixel: int, tile_box: tuple[int, int, int, int], tile_wh: int
) -> bytes:
    x, y, w, h = tile_box
    tile_stride = tile_wh * bytes_per_pixel
    tile_data = bytearray(tile_stride * tile_wh)
    src_row_bytes = w * bytes_per_pixel
    for row in range(h):
        src_offset = (y + row) * src_stride + x * bytes_per_pixel
        dst_offset = row * tile_stride
        tile_data[dst_offset : dst_offset + src_row_bytes] = data[src_offset : src_offset + src_row_bytes]
        if w < tile_wh:  # replicate the edge pixel, padding with zeros bleeds into the image via chroma subsampling
            edge_pixel = tile_data[dst_offset + src_row_bytes - bytes_per_pixel : dst_offset + src_row_bytes]
            tile_data[dst_offset + src_row_bytes : dst_offset + tile_stride] = edge_pixel * (tile_wh - w)
    if h < tile_wh:
        edge_row = tile_data[(h - 1) * tile_stride : h * tile_stride]
        for row in range(h, tile_wh):
            tile_data[row * tile_stride : (row + 1) * tile_stride] = edge_row
    return bytes(tile_data)


def _add_planes(  # pylint: disable=too-many-arguments disable=too-many-positional-arguments
    im_out, size: tuple[int, int], mode: str, data, stride: int, bit_depth_out: int
) -> None:
    bit_depth_in = MODE_INFO[mode][1]
    if MODE_INFO[mode][0] == 1:
        im_out.add_plane_l(size, bit_depth_out, bit_depth_in, data, stride, HeifChannel.CHANNEL_Y)
    elif MODE_INFO[mode][0] == 2:
        im_out.add_plane_la(size, bit_depth_out, bit_depth_in, data, stride)
    else:
        im_out.add_plane(size, bit_depth_out, bit_depth_in, data, mode.find("BGR") != -1, stride)


def _output_bit_depth(mode: str, **kwargs) -> int:
    bit_depth_out = 8 if MODE_INFO[mode][1] == 8 else kwargs.get("bit_depth", 16)
    if bit_depth_out == 16:
        bit_depth_out = 12 if options.SAVE_HDR_TO_12_BIT else 10
    return bit_depth_out


def _output_nclx_params(kwargs: dict, nclx_profile=None) -> tuple[int, int, int, int]:
    nclx_keys = ("color_primaries", "transfer_characteristics", "matrix_coefficients", "full_range_flag")
    save_nclx = kwargs.get("save_nclx_profile", options.SAVE_NCLX_PROFILE)
    has_explicit_nclx = any(k in kwargs for k in nclx_keys)
    if save_nclx and nclx_profile and not has_explicit_nclx:
        return (
            nclx_profile["color_primaries"],
            nclx_profile["transfer_characteristics"],
            nclx_profile["matrix_coefficients"],
            nclx_profile["full_range_flag"],
        )
    # When NCLX saving is enabled and no existing NCLX profile is on the image and no explicit NCLX parameters
    # were provided, write an NCLX box that matches libheif internal sRGB encoding defaults.
    # Without this, no NCLX box is written and viewers must guess the color space, which causes color shifts.
    # See issue #365.
    # Values match libheif nclx_profile::set_sRGB_defaults() exactly:
    #   primaries=1 (BT.709)
    #   transfer=13 (sRGB)
    #   matrix=6 (BT.601-6)
    #   full_range=1
    if save_nclx and not kwargs.get("nclx_profile") and not has_explicit_nclx:
        return 1, 13, 6, 1
    return (
        kwargs.get("color_primaries", -1),
        kwargs.get("transfer_characteristics", -1),
        kwargs.get("matrix_coefficients", -1),
        kwargs.get("full_range_flag", -1),
    )


class CtxEncode:
    """Encoder bindings from python to python C module."""

    def __init__(self, compression_format: HeifCompressionFormat, **kwargs):
        quality = kwargs.get("quality", options.QUALITY)
        self.ctx_write = _pillow_heif.CtxWrite(
            compression_format,
            -2 if quality is None else quality,
            options.PREFERRED_ENCODER.get("HEIF" if compression_format == HeifCompressionFormat.HEVC else "AVIF", ""),
        )
        enc_params = kwargs.get("enc_params", {})
        chroma = None
        if "subsampling" in kwargs:
            chroma = SUBSAMPLING_CHROMA_MAP.get(kwargs["subsampling"])
        if chroma is None:
            chroma = kwargs.get("chroma")
        if chroma:
            enc_params["chroma"] = chroma
        for key, value in enc_params.items():
            self.ctx_write.set_parameter(key, value if isinstance(value, str) else str(value))
        self._grid_images: list = []  # the `output_nclx_color_profile` of a grid must outlive `finalize`
        self._tiles_count = 0

    def add_image(self, size: tuple[int, int], mode: str, data, **kwargs) -> None:
        """Adds image to the encoder."""
        if size[0] <= 0 or size[1] <= 0:
            raise ValueError("Empty images are not supported.")
        tile_size = kwargs.pop("tile_size", None)
        if tile_size is None:  # for tiled images the grid structure is preserved during re-save by default
            tile_size = (kwargs.get("tiling") or {}).get("tile_width", 0) or options.GRID_TILE_SIZE
        # libheif cannot mark grid items as premultiplied, such images are encoded as a single image.
        premultiplied_alpha = mode.split(sep=";")[0][-1] == "a"
        if tile_size > 0 and not premultiplied_alpha and (size[0] > tile_size or size[1] > tile_size):
            self._add_image_grid(size, mode, data, tile_size, **kwargs)
        else:
            self._add_image_single(size, mode, data, **kwargs)

    def _add_image_single(self, size: tuple[int, int], mode: str, data, **kwargs) -> None:
        premultiplied_alpha = int(mode.split(sep=";")[0][-1] == "a")
        # creating image
        im_out = self.ctx_write.create_image(size, MODE_INFO[mode][2], MODE_INFO[mode][3], premultiplied_alpha)
        # image data
        _add_planes(im_out, size, mode, data, kwargs.get("stride", 0), _output_bit_depth(mode, **kwargs))
        self._finish_add_image(im_out, size, **kwargs)

    def _add_image_grid(self, size: tuple[int, int], mode: str, data, tile_size: int, **kwargs) -> None:
        tile_columns = ceil(size[0] / tile_size)
        tile_rows = ceil(size[1] / tile_size)
        if tile_columns > 256 or tile_rows > 256:  # the ISO grid payload stores tile counts as uint8
            raise ValueError("Grid image cannot have more than 256 rows or columns, increase `tile_size`.")
        self._tiles_count += tile_columns * tile_rows
        if self._tiles_count > 999:  # default libheif security limit during reading is 1000 items per file
            raise ValueError("File with grid images cannot have more than 999 tiles, increase `tile_size`.")
        grid_handle = self.ctx_write.create_grid(
            size[0],
            size[1],
            tile_columns,
            tile_rows,
            kwargs.get("save_nclx_profile", options.SAVE_NCLX_PROFILE),
            *_output_nclx_params(kwargs, kwargs.get("nclx_profile")),
            kwargs.get("image_orientation", 1),
        )
        self._add_grid_tiles(grid_handle, size, mode, data, tile_size=tile_size, **kwargs)
        pixel_aspect_ratio = kwargs.get("pixel_aspect_ratio")
        if pixel_aspect_ratio:
            grid_handle.set_pixel_aspect_ratio(pixel_aspect_ratio[0], pixel_aspect_ratio[1])
        if kwargs.get("primary"):
            grid_handle.set_primary(self.ctx_write)
        self._add_metadata(grid_handle, **kwargs)
        thumbnails = [i for i in kwargs.get("thumbnails", []) if max(size) > i > 3]
        if thumbnails:
            pixels_im = self.ctx_write.create_image(size, MODE_INFO[mode][2], MODE_INFO[mode][3], 0)
            _add_planes(pixels_im, size, mode, data, kwargs.get("stride", 0), _output_bit_depth(mode, **kwargs))
            image_orientation = kwargs.get("image_orientation", 1)
            for thumb_box in thumbnails:
                grid_handle.encode_thumbnail(self.ctx_write, thumb_box, image_orientation, pixels_im)
        self._grid_images.append(grid_handle)

    def _add_grid_tiles(self, grid_handle, size: tuple[int, int], mode: str, data, **kwargs) -> None:
        tile_size = kwargs["tile_size"]
        bit_depth_out = _output_bit_depth(mode, **kwargs)
        bytes_per_pixel = MODE_INFO[mode][0] * (2 if MODE_INFO[mode][1] > 8 else 1)
        src_stride = kwargs.get("stride", 0) or (size[0] * bytes_per_pixel)
        if len(data) < src_stride * (size[1] - 1) + size[0] * bytes_per_pixel:
            raise ValueError("Image plane does not contain enough data.")
        icc_profile = kwargs.get("icc_profile")
        tile_wh = (tile_size, tile_size)
        for row in range(ceil(size[1] / tile_size)):
            for col in range(ceil(size[0] / tile_size)):
                tile_box = (
                    col * tile_size,
                    row * tile_size,
                    min(tile_size, size[0] - col * tile_size),
                    min(tile_size, size[1] - row * tile_size),
                )
                tile_data = _extract_tile(data, src_stride, bytes_per_pixel, tile_box, tile_size)
                tile_im = self.ctx_write.create_image(
                    tile_wh, MODE_INFO[mode][2], MODE_INFO[mode][3], int(mode.split(sep=";")[0][-1] == "a")
                )
                _add_planes(tile_im, tile_wh, mode, tile_data, 0, bit_depth_out)
                if icc_profile is not None:
                    tile_im.set_icc_profile(kwargs.get("icc_profile_type", "prof"), icc_profile)
                self.ctx_write.add_tile(grid_handle, col, row, tile_im)

    def add_image_ycbcr(self, img: Image.Image, **kwargs) -> None:
        """Adds image in `YCbCR` mode to the encoder."""
        tile_size = kwargs.pop("tile_size", None)
        if tile_size is None:
            tile_size = options.GRID_TILE_SIZE
        if tile_size > 0 and (img.size[0] > tile_size or img.size[1] > tile_size):
            raise ValueError("Grid encoding is not supported for `YCbCr` mode images, set `tile_size=0`.")
        # creating image
        im_out = self.ctx_write.create_image(img.size, MODE_INFO[img.mode][2], MODE_INFO[img.mode][3], 0)
        # image data
        for i in (HeifChannel.CHANNEL_Y, HeifChannel.CHANNEL_CB, HeifChannel.CHANNEL_CR):
            im_out.add_plane_l(img.size, 8, 8, bytes(img.getdata(i)), kwargs.get("stride", 0), i)
        self._finish_add_image(im_out, img.size, **kwargs)

    def _finish_add_image(self, im_out, size: tuple[int, int], **kwargs):
        # set ICC color profile
        icc_profile = kwargs.get("icc_profile")
        if icc_profile is not None:
            im_out.set_icc_profile(kwargs.get("icc_profile_type", "prof"), icc_profile)
        # set NCLX color profile
        if kwargs.get("nclx_profile"):
            im_out.set_nclx_profile(
                *[
                    kwargs["nclx_profile"][i]
                    for i in ("color_primaries", "transfer_characteristics", "matrix_coefficients", "full_range_flag")
                ]
            )
        # set pixel aspect ratio
        pixel_aspect_ratio = kwargs.get("pixel_aspect_ratio")
        if pixel_aspect_ratio:
            im_out.set_pixel_aspect_ratio(pixel_aspect_ratio[0], pixel_aspect_ratio[1])
        # encode
        image_orientation = kwargs.get("image_orientation", 1)
        im_out.encode(
            self.ctx_write,
            kwargs.get("primary", False),
            kwargs.get("save_nclx_profile", options.SAVE_NCLX_PROFILE),
            *_output_nclx_params(kwargs),
            image_orientation,
        )
        # adding metadata
        self._add_metadata(im_out, **kwargs)
        # adding thumbnails
        for thumb_box in kwargs.get("thumbnails", []):
            if max(size) > thumb_box > 3:
                im_out.encode_thumbnail(self.ctx_write, thumb_box, image_orientation)

    def _add_metadata(self, im_out, **kwargs) -> None:
        exif = kwargs.get("exif")
        if exif is not None:
            if isinstance(exif, Image.Exif):
                exif = exif.tobytes()
            im_out.set_exif(self.ctx_write, exif)
        xmp = kwargs.get("xmp")
        if xmp is not None:
            im_out.set_xmp(self.ctx_write, xmp)
        for metadata in kwargs.get("metadata", []):
            im_out.set_metadata(self.ctx_write, metadata["type"], metadata["content_type"], metadata["data"])

    def save(self, fp) -> None:
        """Ask encoder to produce output based on previously added images."""
        data = self.ctx_write.finalize()
        self._grid_images.clear()
        if isinstance(fp, (str, Path)):
            Path(fp).write_bytes(data)
        elif hasattr(fp, "write"):
            fp.write(data)
        else:
            raise TypeError("`fp` must be a path to file or an object with `write` method.")


@dataclass
class MimCImage:
    """Mimicry of the HeifImage class."""

    def __init__(self, mode: str, size: tuple[int, int], data: bytes, **kwargs):
        self.mode = mode
        self.size = size
        self.stride: int = kwargs.get("stride", size[0] * MODE_INFO[mode][0] * ceil(MODE_INFO[mode][1] / 8))
        self.data = data
        self.metadata: list[dict] = []
        self.color_profile = None
        self.thumbnails: list[int] = []
        self.depth_image_list: list = []
        self.aux_image_ids: list[int] = []
        self.primary = False
        self.chroma = HeifChroma.UNDEFINED.value
        self.colorspace = HeifColorspace.UNDEFINED.value
        self.pixel_aspect_ratio = None
        self.camera_intrinsic_matrix = None
        self.camera_extrinsic_matrix_rot = None
        self.tiling = None

    @property
    def size_mode(self):
        """Mimicry of c_image property."""
        return self.size, self.mode

    @property
    def bit_depth(self) -> int:
        """Return bit-depth based on image mode."""
        return MODE_INFO[self.mode][1]


def load_libheif_plugin(plugin_path: str | Path) -> None:
    """Load specified LibHeif plugin."""
    _pillow_heif.load_plugin(plugin_path)
