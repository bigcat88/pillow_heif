"""
Functions and classes for heif images to read.
"""


import builtins
import pathlib
from functools import partial
from warnings import warn

from _pillow_heif_cffi import ffi, lib

from .constants import (
    HeifFiletype,
    HeifColorProfileType,
    HeifChroma,
    HeifChannel,
    HeifColorspace,
    HeifBrand,
)
from .error import check_libheif_error
from ._options import OPTIONS


class HeifFile:
    def __init__(
        self,
        *,
        size: tuple,
        has_alpha: bool,
        bit_depth: int,
        data,
        stride,
        **kwargs,
    ):
        self.size = size
        self.has_alpha = has_alpha
        self.mode = "RGBA" if has_alpha else "RGB"
        self.bit_depth = bit_depth
        self.data = data
        self.stride = stride
        self.brand = kwargs.get("brand", HeifBrand.UNKNOWN)
        self.metadata = kwargs.get("metadata", [])
        self.color_profile = kwargs.get("color_profile", {})

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with {str(len(self.data)) + ' bytes' if self.data else 'no'} data>"
        )

    def load(self):
        return self  # already loaded

    def close(self) -> None:
        self.data = None


class UndecodedHeifFile(HeifFile):
    def __init__(self, heif_handle, *, apply_transformations: bool, convert_hdr_to_8bit: bool, **kwargs):
        self._heif_handle = heif_handle
        self.apply_transformations = apply_transformations
        self.convert_hdr_to_8bit = convert_hdr_to_8bit
        super().__init__(data=None, stride=None, **kwargs)

    def load(self):
        self.data, self.stride = _read_heif_image(self._heif_handle, self)
        self.close()
        self.__class__ = HeifFile
        return self

    def close(self) -> None:
        # Don't call super().close() here, we don't need to free bytes.
        if hasattr(self, "_heif_handle"):
            del self._heif_handle


def check_heif(fp):
    """
    Wrapper around `libheif.heif_check_filetype`.

    Note: If `fp` contains less 12 bytes, then returns `HeifFiletype.NO`.

    :param fp: A filename (string), pathlib.Path object, file object or bytes.
       The file object must implement ``file.read`` and ``file.seek`` methods,
       and be opened in binary mode.
    :returns: `HeifFiletype`
    """
    magic = _get_bytes(fp, 12)
    return HeifFiletype.NO if len(magic) < 12 else lib.heif_check_filetype(magic, len(magic))


def is_supported(fp) -> bool:
    """
    Checks if `fp` contains a supported file type, by calling :py:func:`~pillow_heif.reader.check_heif` function.
    If `heif_filetype_yes_supported` or `heif_filetype_maybe` then returns True.
    If `heif_filetype_no` then returns False.
    OPTIONS
    "strict" value determine what to return for `heif_filetype_yes_unsupported`.
    "avif" value determine will be `avif` files marked as supported.
    """
    magic = _get_bytes(fp, 12)
    heif_filetype = check_heif(magic)
    if heif_filetype == HeifFiletype.NO or (not OPTIONS["avif"] and magic[8:12] in (b"avif", b"avis")):
        return False
    if heif_filetype in (HeifFiletype.YES_SUPPORTED, HeifFiletype.MAYBE):
        return True
    return not OPTIONS["strict"]


def open_heif(fp, *, apply_transformations: bool = True, convert_hdr_to_8bit: bool = True) -> UndecodedHeifFile:
    d = _get_bytes(fp)
    ctx = lib.heif_context_alloc()
    collect = _keep_refs(lib.heif_context_free, data=d)
    ctx = ffi.gc(ctx, collect, size=len(d))
    return _read_heif_context(ctx, d, apply_transformations, convert_hdr_to_8bit)


def read_heif(fp, *, apply_transformations: bool = True, convert_hdr_to_8bit: bool = True) -> HeifFile:
    heif_file = open_heif(
        fp,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
    )
    return heif_file.load()


def _get_bytes(fp, length=None):
    if isinstance(fp, (str, pathlib.Path)):
        with builtins.open(fp, "rb") as f:
            return f.read(length or -1)
    if hasattr(fp, "read"):
        return fp.read(length or -1)
    return bytes(fp)[:length]


def _keep_refs(destructor, **refs):
    """
    Keep refs to passed arguments until `inner` callback exist.
    This prevents collecting parent objects until all children are collected.
    """

    def inner(cdata):
        return destructor(cdata)

    inner._refs = refs
    return inner


def _read_heif_context(ctx, d, apply_transformations: bool, convert_hdr_to_8bit: bool) -> UndecodedHeifFile:
    brand = lib.heif_main_brand(d[:12], 12)
    error = lib.heif_context_read_from_memory_without_copy(ctx, d, len(d), ffi.NULL)
    check_libheif_error(error)
    p_handle = ffi.new("struct heif_image_handle **")
    error = lib.heif_context_get_primary_image_handle(ctx, p_handle)
    check_libheif_error(error)
    collect = _keep_refs(lib.heif_image_handle_release, ctx=ctx)
    handle = ffi.gc(p_handle[0], collect)
    return _read_heif_handle(handle, apply_transformations, convert_hdr_to_8bit, brand=brand)


def _read_heif_handle(handle, apply_transformations: bool, convert_hdr_to_8bit: bool, **kwargs) -> UndecodedHeifFile:
    width = lib.heif_image_handle_get_width(handle)
    height = lib.heif_image_handle_get_height(handle)
    has_alpha = bool(lib.heif_image_handle_has_alpha_channel(handle))
    bit_depth = lib.heif_image_handle_get_luma_bits_per_pixel(handle)
    metadata = _read_metadata(handle)
    color_profile = _read_color_profile(handle)
    return UndecodedHeifFile(
        handle,
        size=(width, height),
        has_alpha=has_alpha,
        bit_depth=bit_depth,
        metadata=metadata,
        color_profile=color_profile,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
        **kwargs,
    )


def _read_metadata(handle) -> list:
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


def _read_color_profile(handle) -> dict:
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


def _read_heif_image(handle, heif_file):
    colorspace = HeifColorspace.RGB
    if heif_file.convert_hdr_to_8bit or heif_file.bit_depth <= 8:
        chroma = HeifChroma.INTERLEAVED_RGBA if heif_file.has_alpha else HeifChroma.INTERLEAVED_RGB
    else:
        if heif_file.has_alpha:
            chroma = HeifChroma.INTERLEAVED_RRGGBBAA_BE
        else:
            chroma = HeifChroma.INTERLEAVED_RRGGBB_BE
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
    p_data = lib.heif_image_get_plane_readonly(img, HeifChannel.INTERLEAVED, p_stride)
    stride = p_stride[0]
    data_length = heif_file.size[1] * stride
    # Release image as soon as no references to p_data left
    collect = partial(_release_heif_image, img)
    p_data = ffi.gc(p_data, collect, size=data_length)
    # ffi.buffer obligatory keeps a reference to p_data
    data_buffer = ffi.buffer(p_data, data_length)
    return data_buffer, stride


def _release_heif_image(img, _p_data=None) -> None:
    lib.heif_image_release(img)


# --------------------------------------------------------------------
# DEPRECATED FUNCTIONS.


def check(fp):
    warn("Function `check` is deprecated, use `check_heif` instead.", DeprecationWarning)
    return check_heif(fp)  # pragma: no cover


def open(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):  # pylint: disable=redefined-builtin
    warn("Function `open` is deprecated, use `open_heif` instead.", DeprecationWarning)
    return open_heif(
        fp, apply_transformations=apply_transformations, convert_hdr_to_8bit=convert_hdr_to_8bit
    )  # pragma: no cover


def read(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    warn("Function `read` is deprecated, use `read_heif` instead.", DeprecationWarning)
    return read_heif(
        fp, apply_transformations=apply_transformations, convert_hdr_to_8bit=convert_hdr_to_8bit
    )  # pragma: no cover
