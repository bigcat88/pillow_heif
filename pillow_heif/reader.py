import functools
import pathlib
import warnings

from . import constants as _constants
from . import error as _error
from . import _libheif


class HeifFile:
    def __init__(self, *, size, data, metadata, color_profile, has_alpha, bit_depth, stride):
        self.size = size
        self.data = data
        self.metadata = metadata
        self.brand = _constants.heif_brand_unknown_brand
        self.color_profile = color_profile
        self.has_alpha = has_alpha
        self.mode = "RGBA" if has_alpha else "RGB"
        self.bit_depth = bit_depth
        self.stride = stride


def check(fp):
    magic = _get_bytes(fp, 12)
    filetype_check = _libheif.lib.heif_check_filetype(magic, len(magic))
    return filetype_check


def read_heif(fp, apply_transformations=True):
    warnings.warn("read_heif is deprecated, use read instead", DeprecationWarning)
    return read(fp, apply_transformations=apply_transformations)


def read(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    d = _get_bytes(fp)
    result = _read_heif_bytes(d, apply_transformations, convert_hdr_to_8bit)
    return result


def _get_bytes(fp, length=None):
    if isinstance(fp, str):
        with open(fp, "rb") as f:
            d = f.read(length or -1)
    elif isinstance(fp, pathlib.Path):
        with fp.open('rb') as f:
            d = f.read(length or -1)
    elif hasattr(fp, "read"):
        d = fp.read(length or -1)
    else:
        d = bytes(fp)[:length]
    return d


def _read_heif_bytes(d, apply_transformations, convert_hdr_to_8bit):
    magic = d[:12]
    filetype_check = _libheif.lib.heif_check_filetype(magic, len(magic))
    if filetype_check == _constants.heif_filetype_no:
        raise ValueError("Input is not a HEIF/AVIF file")
    elif filetype_check == _constants.heif_filetype_yes_unsupported:
        warnings.warn("Input is an unsupported HEIF/AVIF file type - trying anyway!")
    ctx = _libheif.lib.heif_context_alloc()
    try:
        result = _read_heif_context(ctx, d, apply_transformations, convert_hdr_to_8bit)
        result.brand = _libheif.lib.heif_main_brand(magic, len(magic))
    finally:
        _libheif.lib.heif_context_free(ctx)
    return result


def _read_heif_context(ctx, d, apply_transformations, convert_hdr_to_8bit):
    error = _libheif.lib.heif_context_read_from_memory_without_copy(ctx, d, len(d), _libheif.ffi.NULL)
    if error.code != 0:
        raise _error.HeifError(
            code=error.code, subcode=error.subcode, message=_libheif.ffi.string(error.message).decode(),)
    p_handle = _libheif.ffi.new("struct heif_image_handle **")
    error = _libheif.lib.heif_context_get_primary_image_handle(ctx, p_handle)
    if error.code != 0:
        raise _error.HeifError(
            code=error.code, subcode=error.subcode, message=_libheif.ffi.string(error.message).decode(),)
    handle = p_handle[0]
    try:
        result = _read_heif_handle(handle, apply_transformations, convert_hdr_to_8bit)
    finally:
        _libheif.lib.heif_image_handle_release(handle)
    return result


def _read_heif_handle(handle, apply_transformations, convert_hdr_to_8bit):
    width = _libheif.lib.heif_image_handle_get_width(handle)
    height = _libheif.lib.heif_image_handle_get_height(handle)
    size = (width, height)
    has_alpha = bool(_libheif.lib.heif_image_handle_has_alpha_channel(handle))
    bit_depth = _libheif.lib.heif_image_handle_get_luma_bits_per_pixel(handle)
    colorspace = _constants.heif_colorspace_RGB
    if convert_hdr_to_8bit or bit_depth <= 8:
        if has_alpha:
            chroma = _constants.heif_chroma_interleaved_RGBA
        else:
            chroma = _constants.heif_chroma_interleaved_RGB
    else:
        if has_alpha:
            chroma = _constants.heif_chroma_interleaved_RRGGBBAA_BE
        else:
            chroma = _constants.heif_chroma_interleaved_RRGGBB_BE
    p_options = _libheif.lib.heif_decoding_options_alloc()
    p_options.ignore_transformations = int(not apply_transformations)
    p_options.convert_hdr_to_8bit = int(convert_hdr_to_8bit)
    p_img = _libheif.ffi.new("struct heif_image **")
    error = _libheif.lib.heif_decode_image(handle, p_img, colorspace, chroma, p_options,)
    _libheif.lib.heif_decoding_options_free(p_options)
    if error.code != 0:
        raise _error.HeifError(
            code=error.code, subcode=error.subcode, message=_libheif.ffi.string(error.message).decode(),)
    img = p_img[0]
    data, stride = _read_heif_image(img, height)
    metadata = _read_metadata(handle)
    color_profile = _read_color_profile(handle)
    heif_file = HeifFile(
        size=size,
        data=data,
        metadata=metadata,
        color_profile=color_profile,
        has_alpha=has_alpha,
        bit_depth=bit_depth,
        stride=stride,)
    return heif_file


def _read_metadata(handle):
    block_count = _libheif.lib.heif_image_handle_get_number_of_metadata_blocks(handle, _libheif.ffi.NULL)
    if block_count == 0:
        return
    metadata = []
    ids = _libheif.ffi.new("heif_item_id[]", block_count)
    _libheif.lib.heif_image_handle_get_list_of_metadata_block_IDs(handle, _libheif.ffi.NULL, ids, block_count)
    for i in range(len(ids)):
        metadata_type = _libheif.lib.heif_image_handle_get_metadata_type(handle, ids[i])
        metadata_type = _libheif.ffi.string(metadata_type).decode()
        data_length = _libheif.lib.heif_image_handle_get_metadata_size(handle, ids[i])
        if data_length > 0:
            p_data = _libheif.ffi.new("char[]", data_length)
            error = _libheif.lib.heif_image_handle_get_metadata(handle, ids[i], p_data)
            if error.code != 0:
                raise _error.HeifError(
                    code=error.code, subcode=error.subcode, message=_libheif.ffi.string(error.message).decode(),)
            data_buffer = _libheif.ffi.buffer(p_data, data_length)
            data = bytes(data_buffer)
            if metadata_type == "Exif":
                data = data[4:]     # skip TIFF header, first 4 bytes
            metadata.append({"type": metadata_type, "data": data})
    return metadata


def _read_color_profile(handle):
    profile_type = _libheif.lib.heif_image_handle_get_color_profile_type(handle)
    if profile_type == _constants.heif_color_profile_type_not_present:
        return
    if profile_type in (_constants.heif_color_profile_type_rICC, _constants.heif_color_profile_type_prof):
        data_length = _libheif.lib.heif_image_handle_get_raw_color_profile_size(handle)
        if data_length == 0:
            return
        p_data = _libheif.ffi.new("char[]", data_length)
        error = _libheif.lib.heif_image_handle_get_raw_color_profile(handle, p_data)
    elif profile_type == _constants.heif_color_profile_type_nclx:
        pp_data = _libheif.ffi.new("struct heif_color_profile_nclx **")
        data_length = _libheif.ffi.sizeof("struct heif_color_profile_nclx")
        error = _libheif.lib.heif_image_handle_get_nclx_color_profile(handle, pp_data)
        p_data = pp_data[0]
        _libheif.ffi.release(pp_data)
    else:
        raise _error.HeifError(
            code=10, subcode=0, message="Not supported color profile.", )
    if error.code != 0:
        raise _error.HeifError(
            code=error.code, subcode=error.subcode, message=_libheif.ffi.string(error.message).decode(),)
    data_buffer = _libheif.ffi.buffer(p_data, data_length)
    data = bytes(data_buffer)
    if profile_type == _constants.heif_color_profile_type_rICC:
        color_profile = {"type": "rICC", "data": data}
    elif profile_type == _constants.heif_color_profile_type_prof:
        color_profile = {"type": "prof", "data": data}
    else:
        color_profile = {"type": "nclx", "data": data}
    return color_profile


def _read_heif_image(img, height):
    p_stride = _libheif.ffi.new("int *")
    p_data = _libheif.lib.heif_image_get_plane_readonly(img, _constants.heif_channel_interleaved, p_stride)
    stride = p_stride[0]
    data_length = height * stride
    collect = functools.partial(_release_heif_image, img)
    p_data = _libheif.ffi.gc(p_data, collect)
    data_buffer = _libheif.ffi.buffer(p_data, data_length)
    return data_buffer, stride


def _release_heif_image(img, p_data=None):
    _libheif.lib.heif_image_release(img)
