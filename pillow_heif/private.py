"""
Undocumented private functions for other code to look better.
"""
from _pillow_heif_cffi import ffi, lib

from ._libheif_ctx import LibHeifCtxWrite
from .constants import HeifChannel, HeifChroma, HeifColorProfileType, HeifColorspace
from .error import check_libheif_error


def create_image(size: tuple, chroma: HeifChroma, bit_depth: int, mode: str, data, **kwargs):
    width, height = size
    p_new_img = ffi.new("struct heif_image **")
    error = lib.heif_image_create(width, height, kwargs.get("color", HeifColorspace.RGB), chroma, p_new_img)
    check_libheif_error(error)
    new_img = ffi.gc(p_new_img[0], lib.heif_image_release)
    error = lib.heif_image_add_plane(new_img, HeifChannel.INTERLEAVED, width, height, bit_depth)
    check_libheif_error(error)
    p_dest_stride = ffi.new("int *")
    p_data = lib.heif_image_get_plane(new_img, HeifChannel.INTERLEAVED, p_dest_stride)
    dest_stride = p_dest_stride[0]
    copy_image_data(p_data, data, dest_stride, get_stride(bit_depth, mode, width, **kwargs), height)
    return new_img


def copy_image_data(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    if dest_stride == source_stride:
        ffi.memmove(dest_data, src_data, len(src_data))
    else:
        p_source = ffi.from_buffer("uint8_t*", src_data)
        for i in range(height):
            ffi.memmove(dest_data + dest_stride * i, p_source + source_stride * i, source_stride)


def get_stride(bit_depth: int, mode: str, width: int, **kwargs) -> int:
    __stride = kwargs.get("stride", None)
    __factor = 1 if bit_depth == 8 else 2
    return __stride if __stride else width * 3 * __factor if mode == "RGB" else width * 4 * __factor


def heif_ctx_as_dict(bit_depth: int, mode: str, size: tuple, data, **kwargs) -> dict:
    return {
        "bit_depth": bit_depth,
        "mode": mode,
        "size": size,
        "data": data,
        "stride": get_stride(bit_depth, mode, size[0], **kwargs),
        "additional_info": kwargs.get("add_info", {}),
    }


def get_img_depth(img):
    return 8 if getattr(img, "misc", {}).get("to_8bit", None) else img.bit_depth


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
            if not _result and md_block["data"] and md_block["data"][0:4] == b"Exif":
                _result = md_block["data"]
    for i in reversed(_purge):
        del metadata[i]
    return _result


def set_exif(ctx: LibHeifCtxWrite, heif_img_handle, info: dict) -> None:
    if info["exif"] is not None:
        error = lib.heif_context_add_exif_metadata(ctx.ctx, heif_img_handle, info["exif"], len(info["exif"]))
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
        decoded_data_type = ffi.string(metadata_type).decode()
        content_type = ffi.string(lib.heif_image_handle_get_metadata_content_type(handle, block_id))
        data_length = lib.heif_image_handle_get_metadata_size(handle, block_id)
        if data_length > 0:
            p_data = ffi.new("char[]", data_length)
            error = lib.heif_image_handle_get_metadata(handle, block_id, p_data)
            check_libheif_error(error)
            data_buffer = ffi.buffer(p_data, data_length)
            data = bytes(data_buffer)
            if decoded_data_type == "Exif":
                data = data[4:]  # skip TIFF header, first 4 bytes
            metadata.append(
                {"type": decoded_data_type, "data": data, "metadata_type": metadata_type, "content_type": content_type}
            )
    return metadata


def set_metadata(ctx: LibHeifCtxWrite, heif_img_handle, info: dict) -> None:
    for metadata in info["metadata"]:
        error = lib.heif_context_add_generic_metadata(
            ctx.ctx,
            heif_img_handle,
            metadata["data"],
            len(metadata["data"]),
            metadata["metadata_type"],
            metadata["content_type"],
        )
        check_libheif_error(error)
