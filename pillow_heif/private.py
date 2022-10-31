"""
Undocumented private functions for other code to look better.
"""

from math import ceil
from typing import Union

from _pillow_heif_cffi import ffi, lib
from PIL import __version__ as pil_version

from ._libheif_ctx import LibHeifCtxWrite
from .constants import HeifChroma, HeifColorProfileType, HeifColorspace
from .error import check_libheif_error

FFI_DRY_ALLOC = ffi.new_allocator(should_clear_after_alloc=False)


# from dataclasses import dataclass
# @dataclass                # Available from Python 3.7
class HeifCtxAsDict:  # noqa # pylint: disable=too-few-public-methods
    """Representation of one image"""

    def __init__(self, mode: str, size: tuple, data, **kwargs):
        stride = kwargs.get("stride", None)
        if stride is None:
            stride = get_pure_stride(mode, size[0])
        self.mode = mode
        self.size = size
        self.data = data
        self.stride = stride
        self.additional_info = kwargs.get("add_info", {})


def get_pure_stride(mode: str, width: int):
    return width * MODE_INFO[mode][0] * ceil(MODE_INFO[mode][1] / 8)


MODE_CONVERT = {
    # source_mode: {target_mode: convert_function,}
    "BGRA;16": {"RGBA;10": lib.convert_bgra16_to_rgba10, "RGBA;12": lib.convert_bgra16_to_rgba12},
    "BGRa;16": {"RGBa;10": lib.convert_bgra16_to_rgba10, "RGBa;12": lib.convert_bgra16_to_rgba12},
    "BGR;16": {"RGB;10": lib.convert_bgr16_to_rgb10, "RGB;12": lib.convert_bgr16_to_rgb12},
    "RGBA;16": {
        "RGBA;10": lib.convert_rgba16_to_rgba10,
        "RGBA;12": lib.convert_rgba16_to_rgba12,
        "RGBA": lib.convert_rgba16_to_rgba,
    },
    "RGBa;16": {
        "RGBa;10": lib.convert_rgba16_to_rgba10,
        "RGBa;12": lib.convert_rgba16_to_rgba12,
    },
    "RGB;16": {"RGB;10": lib.convert_rgb16_to_rgb10, "RGB;12": lib.convert_rgb16_to_rgb12},
    "L;16": {"L;10": lib.convert_i16_to_i10, "L;12": lib.convert_i16_to_i12},
    "I;16": {"L;10": lib.convert_i16_to_i10, "L;12": lib.convert_i16_to_i12},
    "I;16L": {"L;10": lib.convert_i16_to_i10, "L;12": lib.convert_i16_to_i12},
    "RGBA;12": {"RGBA;16": lib.convert_rgba12_to_rgba16, "BGRA;16": lib.convert_rgba12_to_bgra16},
    "RGBa;12": {"RGBa;16": lib.convert_rgba12_to_rgba16, "BGRa;16": lib.convert_rgba12_to_bgra16},
    "RGB;12": {"RGB;16": lib.convert_rgb12_to_rgb16, "BGR;16": lib.convert_rgb12_to_bgr16},
    "RGBA;10": {"RGBA;16": lib.convert_rgba10_to_rgba16, "BGRA;16": lib.convert_rgba10_to_bgra16},
    "RGBa;10": {"RGBa;16": lib.convert_rgba10_to_rgba16, "BGRa;16": lib.convert_rgba10_to_bgra16},
    "RGB;10": {"RGB;16": lib.convert_rgb10_to_rgb16, "BGR;16": lib.convert_rgb10_to_bgr16},
    "BGRA": {"RGBA": lib.convert_bgra_rgba},
    "BGRa": {"RGBa": lib.convert_bgra_rgba},
    "BGR": {"RGB": lib.convert_bgr_rgb},
    "RGBA": {
        "BGRA": lib.convert_bgra_rgba,
        "RGBA;16": lib.convert_rgba_to_rgba16,
        "BGRA;16": lib.convert_rgba_to_bgra16,
    },
    "RGBa": {
        "BGRa": lib.convert_bgra_rgba,
        "RGBa;16": lib.convert_rgba_to_rgba16,
        "BGRa;16": lib.convert_rgba_to_bgra16,
        "RGB": lib.convert_rgba_premultiplied_to_rgb,
        "BGR": lib.convert_rgba_premultiplied_to_bgr,
    },
    "RGB": {"BGR": lib.convert_bgr_rgb, "RGB;16": lib.convert_rgb_to_rgb16, "BGR;16": lib.convert_rgb_to_bgr16},
}


MODE_INFO = {
    # name -> [channels, bits per pixel channel, colorspace, chroma, (mode_for_saving 10,12 bit), numpy_typestr]
    "BGRA;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, ("RGBA;10", "RGBA;12"), "<u2"),
    "BGRa;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, ("RGBa;10", "RGBa;12"), "<u2"),
    "BGR;16": (3, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE, ("RGB;10", "RGB;12"), "<u2"),
    "RGBA;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, ("RGBA;10", "RGBA;12"), "<u2"),
    "RGBa;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, ("RGBa;10", "RGBa;12"), "<u2"),
    "RGB;16": (3, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE, ("RGB;10", "RGB;12"), "<u2"),
    "L;16": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, ("L;10", "L;12"), "<u2"),
    "I;16": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, ("L;10", "L;12"), "<u2"),
    "I;16L": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, ("L;10", "L;12"), "<u2"),
    "RGBA;12": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, None, "<u2"),
    "RGBa;12": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, None, "<u2"),
    "RGB;12": (3, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE, None, "<u2"),
    "RGBA;12B": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_BE, None, ">u2"),
    "RGBa;12B": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_BE, None, ">u2"),
    "RGB;12B": (3, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_BE, None, ">u2"),
    "L;12": (1, 12, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, None, "<u2"),
    "RGBA;10": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, None, "<u2"),
    "RGBa;10": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, None, "<u2"),
    "RGB;10": (3, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE, None, "<u2"),
    "RGBA;10B": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_BE, None, ">u2"),
    "RGBa;10B": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_BE, None, ">u2"),
    "RGB;10B": (3, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_BE, None, ">u2"),
    "L;10": (1, 10, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, None, "<u2"),
    "RGBA": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA, None, "|u1"),
    "RGBa": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA, None, "|u1"),
    "RGB": (3, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGB, None, "|u1"),
    "BGRA": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA, "RGBA", "|u1"),
    "BGRa": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA, "RGBa", "|u1"),
    "BGR": (3, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGB, "RGB", "|u1"),
    "L": (1, 8, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, None, "|u1"),
    "": (0, 0, HeifColorspace.UNDEFINED, HeifChroma.UNDEFINED, None, ""),
}


def read_color_profile(handle) -> dict:
    profile_type = lib.heif_image_handle_get_color_profile_type(handle)
    if profile_type == HeifColorProfileType.NOT_PRESENT:
        return {}
    if profile_type == HeifColorProfileType.NCLX:
        _type = "nclx"
        pp_data = ffi.new("struct heif_color_profile_nclx **")
        data_length = ffi.sizeof("struct heif_color_profile_nclx")
        error = lib.heif_image_handle_get_nclx_color_profile(handle, pp_data)
        p_data = pp_data[0]
        ffi.release(pp_data)
    else:
        _type = "prof" if profile_type == HeifColorProfileType.PROF else "rICC"
        data_length = lib.heif_image_handle_get_raw_color_profile_size(handle)
        if data_length == 0:
            return {"type": _type, "data": b""}
        p_data = ffi.new("char[]", data_length)
        error = lib.heif_image_handle_get_raw_color_profile(handle, p_data)
    check_libheif_error(error)
    data_buffer = ffi.buffer(p_data, data_length)
    return {"type": _type, "data": bytes(data_buffer)}


def set_color_profile(heif_img, info: dict) -> None:
    __icc_profile = info.get("icc_profile", None)
    if __icc_profile is not None:
        _prof_type = info.get("icc_profile_type", "prof").encode("ascii")
        error = lib.heif_image_set_raw_color_profile(
            heif_img, _prof_type, info["icc_profile"], len(info["icc_profile"])
        )
        check_libheif_error(error)
    elif info.get("nclx_profile", None):
        error = lib.heif_image_set_nclx_color_profile(
            heif_img,
            ffi.cast("const struct heif_color_profile_nclx*", ffi.from_buffer(info["nclx_profile"])),
        )
        check_libheif_error(error)


def retrieve_exif(metadata: list):
    _result = None
    _purge = []
    for i, md_block in enumerate(metadata):
        if md_block["type"] == "Exif":
            _purge.append(i)
            if not _result and md_block["data"]:
                _result = md_block["data"]
    for i in reversed(_purge):
        del metadata[i]
    return _result


def set_exif(ctx: LibHeifCtxWrite, heif_img_handle, exif: Union[bytes, None]) -> None:
    if exif is not None:
        error = lib.heif_context_add_exif_metadata(ctx.ctx, heif_img_handle, exif, len(exif))
        check_libheif_error(error)


def retrieve_xmp(metadata: list):
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


def set_xmp(ctx: LibHeifCtxWrite, heif_img_handle, xmp: Union[bytes, None]) -> None:
    if xmp is not None:
        error = lib.heif_context_add_XMP_metadata(ctx.ctx, heif_img_handle, xmp, len(xmp))
        check_libheif_error(error)


def read_metadata(handle) -> list:
    block_count = lib.heif_image_handle_get_number_of_metadata_blocks(handle, ffi.NULL)
    if block_count == 0:
        return []
    metadata = []
    blocks_ids = ffi.new("heif_item_id[]", block_count)
    lib.heif_image_handle_get_list_of_metadata_block_IDs(handle, ffi.NULL, blocks_ids, block_count)
    for block_id in blocks_ids:
        metadata_type = lib.heif_image_handle_get_metadata_type(handle, block_id)
        metadata_type = ffi.string(metadata_type).decode("utf-8")
        content_type = ffi.string(lib.heif_image_handle_get_metadata_content_type(handle, block_id))
        data_length = lib.heif_image_handle_get_metadata_size(handle, block_id)
        if data_length > 0:
            p_data = ffi.new("char[]", data_length)
            error = lib.heif_image_handle_get_metadata(handle, block_id, p_data)
            check_libheif_error(error)
            data_buffer = ffi.buffer(p_data, data_length)
            data = bytes(data_buffer)
            if metadata_type == "Exif":
                data = data[4:]  # skip TIFF header, first 4 bytes
            metadata.append({"type": metadata_type, "data": data, "content_type": content_type})
    return metadata


def set_metadata(ctx: LibHeifCtxWrite, heif_img_handle, info: dict) -> None:
    for metadata in info["metadata"]:
        error = lib.heif_context_add_generic_metadata(
            ctx.ctx,
            heif_img_handle,
            metadata["data"],
            len(metadata["data"]),
            metadata["type"].encode("utf-8"),
            metadata["content_type"],
        )
        check_libheif_error(error)


def exif_from_pillow(additional_info: dict, frame) -> None:
    if "exif" not in additional_info:
        if hasattr(frame, "getexif"):
            if pil_version[:2] not in ("6.", "7.", "8.") and pil_version[:4] not in ("9.0.", "9.1."):
                exif = frame.getexif()
                if exif:
                    additional_info["exif"] = exif.tobytes()


def xmp_from_pillow(additional_info: dict, frame) -> None:
    if "xmp" not in additional_info:
        if "XML:com.adobe.xmp" in frame.info:  # PNG
            additional_info["xmp"] = frame.info["XML:com.adobe.xmp"]
        elif hasattr(frame, "tag_v2"):  # TIFF
            if 700 in frame.tag_v2:
                additional_info["xmp"] = frame.tag_v2[700]
        elif hasattr(frame, "applist"):  # JPEG
            for segment, content in frame.applist:
                if segment == "APP1":
                    marker, xmp_tags = content.rsplit(b"\x00", 1)
                    if marker == b"http://ns.adobe.com/xap/1.0/":
                        additional_info["xmp"] = xmp_tags
                        break
    if "xmp" in additional_info and isinstance(additional_info["xmp"], str):
        additional_info["xmp"] = additional_info["xmp"].encode("utf-8")
