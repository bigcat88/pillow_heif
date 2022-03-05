"""
Functions and classes for heif images to read.
"""


import builtins
import pathlib
from functools import partial
from warnings import warn

from _pillow_heif_cffi import ffi, lib

from .constants import (
    heif_filetype_no,
    heif_filetype_yes_unsupported,
    heif_color_profile_type_not_present,
    heif_brand_unknown_brand,
    heif_color_profile_type_rICC,
    heif_color_profile_type_prof,
    heif_color_profile_type_nclx,
    heif_colorspace_RGB,
    heif_channel_interleaved,
    heif_chroma_interleaved_RGB,
    heif_chroma_interleaved_RGBA,
    heif_chroma_interleaved_RRGGBB_BE,
    heif_chroma_interleaved_RRGGBBAA_BE,
)
from .error import check_libheif_error


class HeifFile:
    def __init__(self, *, size, has_alpha, bit_depth, metadata, color_profile, data, stride):
        self.size = size
        self.brand = heif_brand_unknown_brand
        self.has_alpha = has_alpha
        self.mode = "RGBA" if has_alpha else "RGB"
        self.bit_depth = bit_depth
        self.metadata = metadata
        self.color_profile = color_profile
        self.data = data
        self.stride = stride

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with {str(len(self.data)) + ' bytes' if self.data else 'no'} data>"
        )

    def load(self):
        return self  # already loaded

    def close(self):
        self.data = None


class UndecodedHeifFile(HeifFile):
    def __init__(self, heif_handle, *, apply_transformations, convert_hdr_to_8bit, **kwargs):
        self._heif_handle = heif_handle
        self.apply_transformations = apply_transformations
        self.convert_hdr_to_8bit = convert_hdr_to_8bit
        super().__init__(data=None, stride=None, **kwargs)

    def load(self):
        self.data, self.stride = _read_heif_image(self._heif_handle, self)
        self.close()
        self.__class__ = HeifFile
        return self

    def close(self):
        # Don't call super().close() here, we don't need to free bytes.
        if hasattr(self, "_heif_handle"):
            del self._heif_handle


def check_heif(fp):
    magic = _get_bytes(fp, 12)
    return lib.heif_check_filetype(magic, len(magic))


def check(fp):
    warn("Function `check` is deprecated, use `check_heif` instead.", DeprecationWarning)
    return check_heif(fp)  # pragma: no cover


def open_heif(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    d = _get_bytes(fp)
    return _read_heif_bytes(d, apply_transformations, convert_hdr_to_8bit)


def open(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):  # pylint: disable=redefined-builtin
    warn("Function `open` is deprecated, use `open_heif` instead.", DeprecationWarning)
    return open_heif(
        fp, apply_transformations=apply_transformations, convert_hdr_to_8bit=convert_hdr_to_8bit
    )  # pragma: no cover


def read_heif(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    heif_file = open_heif(
        fp,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
    )
    return heif_file.load()


def read(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    warn("Function `read` is deprecated, use `read_heif` instead.", DeprecationWarning)
    return read_heif(
        fp, apply_transformations=apply_transformations, convert_hdr_to_8bit=convert_hdr_to_8bit
    )  # pragma: no cover


def _get_bytes(fp, length=None):
    if isinstance(fp, (str, pathlib.Path)):
        with builtins.open(fp, "rb") as f:
            d = f.read(length or -1)
    elif hasattr(fp, "read"):
        d = fp.read(length or -1)
    else:
        d = bytes(fp)[:length]
    return d


def _keep_refs(destructor, **refs):
    """
    Keep refs to passed arguments until `inner` callback exist.
    This prevents collecting parent objects until all children are collected.
    """

    def inner(cdata):
        return destructor(cdata)

    inner._refs = refs
    return inner


def _read_heif_bytes(d, apply_transformations, convert_hdr_to_8bit):
    magic = d[:12]
    filetype_check = lib.heif_check_filetype(magic, len(magic))
    if filetype_check == heif_filetype_no:
        raise ValueError("Input is not a HEIF/AVIF file")
    if filetype_check == heif_filetype_yes_unsupported:
        warn("Input is an unsupported HEIF/AVIF file type - trying anyway!")
    brand = lib.heif_main_brand(magic, len(magic))
    ctx = lib.heif_context_alloc()
    collect = _keep_refs(lib.heif_context_free, data=d)
    ctx = ffi.gc(ctx, collect, size=len(d))
    heif_file = _read_heif_context(ctx, d, apply_transformations, convert_hdr_to_8bit)
    heif_file.brand = brand
    return heif_file


def _read_heif_context(ctx, d, apply_transformations, convert_hdr_to_8bit):
    error = lib.heif_context_read_from_memory_without_copy(ctx, d, len(d), ffi.NULL)
    check_libheif_error(error)
    p_handle = ffi.new("struct heif_image_handle **")
    error = lib.heif_context_get_primary_image_handle(ctx, p_handle)
    check_libheif_error(error)
    collect = _keep_refs(lib.heif_image_handle_release, ctx=ctx)
    handle = ffi.gc(p_handle[0], collect)
    return _read_heif_handle(handle, apply_transformations, convert_hdr_to_8bit)


def _read_heif_handle(handle, apply_transformations, convert_hdr_to_8bit):
    width = lib.heif_image_handle_get_width(handle)
    height = lib.heif_image_handle_get_height(handle)
    has_alpha = bool(lib.heif_image_handle_has_alpha_channel(handle))
    bit_depth = lib.heif_image_handle_get_luma_bits_per_pixel(handle)
    metadata = _read_metadata(handle)
    color_profile = _read_color_profile(handle)
    heif_file = UndecodedHeifFile(
        handle,
        size=(width, height),
        has_alpha=has_alpha,
        bit_depth=bit_depth,
        metadata=metadata,
        color_profile=color_profile,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
    )
    return heif_file


def _read_metadata(handle):
    block_count = lib.heif_image_handle_get_number_of_metadata_blocks(handle, ffi.NULL)
    if block_count == 0:
        return []
    metadata = []
    ids = ffi.new("heif_item_id[]", block_count)
    lib.heif_image_handle_get_list_of_metadata_block_IDs(handle, ffi.NULL, ids, block_count)
    for each_item in ids:
        metadata_type = lib.heif_image_handle_get_metadata_type(handle, each_item)
        metadata_type = ffi.string(metadata_type).decode()
        data_length = lib.heif_image_handle_get_metadata_size(handle, each_item)
        if data_length > 0:
            p_data = ffi.new("char[]", data_length)
            error = lib.heif_image_handle_get_metadata(handle, each_item, p_data)
            check_libheif_error(error)
            data_buffer = ffi.buffer(p_data, data_length)
            data = bytes(data_buffer)
            if metadata_type == "Exif":
                data = data[4:]  # skip TIFF header, first 4 bytes
            metadata.append({"type": metadata_type, "data": data})
    return metadata


def _read_color_profile(handle):
    profile_type = lib.heif_image_handle_get_color_profile_type(handle)
    if profile_type == heif_color_profile_type_not_present:
        return None
    if profile_type == heif_color_profile_type_nclx:
        pp_data = ffi.new("struct heif_color_profile_nclx **")
        data_length = ffi.sizeof("struct heif_color_profile_nclx")
        error = lib.heif_image_handle_get_nclx_color_profile(handle, pp_data)
        p_data = pp_data[0]
        ffi.release(pp_data)
    else:
        data_length = lib.heif_image_handle_get_raw_color_profile_size(handle)
        if data_length == 0:
            return None
        p_data = ffi.new("char[]", data_length)
        error = lib.heif_image_handle_get_raw_color_profile(handle, p_data)
    check_libheif_error(error)
    data_buffer = ffi.buffer(p_data, data_length)
    data = bytes(data_buffer)
    if profile_type == heif_color_profile_type_rICC:
        color_profile = {"type": "rICC", "data": data}
    elif profile_type == heif_color_profile_type_prof:
        color_profile = {"type": "prof", "data": data}
    else:
        color_profile = {"type": "nclx", "data": data}
    return color_profile


def _read_heif_image(handle, heif_file):
    colorspace = heif_colorspace_RGB
    if heif_file.convert_hdr_to_8bit or heif_file.bit_depth <= 8:
        if heif_file.has_alpha:
            chroma = heif_chroma_interleaved_RGBA
        else:
            chroma = heif_chroma_interleaved_RGB
    else:
        if heif_file.has_alpha:
            chroma = heif_chroma_interleaved_RRGGBBAA_BE
        else:
            chroma = heif_chroma_interleaved_RRGGBB_BE
    p_options = lib.heif_decoding_options_alloc()
    p_options = ffi.gc(p_options, lib.heif_decoding_options_free)
    p_options.ignore_transformations = int(not heif_file.apply_transformations)
    p_options.convert_hdr_to_8bit = int(heif_file.convert_hdr_to_8bit)
    p_img = ffi.new("struct heif_image **")
    error = lib.heif_decode_image(
        handle,
        p_img,
        colorspace,
        chroma,
        p_options,
    )
    check_libheif_error(error)
    img = p_img[0]
    p_stride = ffi.new("int *")
    p_data = lib.heif_image_get_plane_readonly(img, heif_channel_interleaved, p_stride)
    stride = p_stride[0]
    data_length = heif_file.size[1] * stride
    # Release image as soon as no references to p_data left
    collect = partial(_release_heif_image, img)
    p_data = ffi.gc(p_data, collect, size=data_length)
    # ffi.buffer obligatory keeps a reference to p_data
    data_buffer = ffi.buffer(p_data, data_length)
    return data_buffer, stride


def _release_heif_image(img, _p_data=None):
    lib.heif_image_release(img)
