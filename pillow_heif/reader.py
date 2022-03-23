"""
Functions and classes for heif images to read.
"""

import builtins
import pathlib
from functools import partial
from typing import Iterator, List, Union
from warnings import warn

from _pillow_heif_cffi import ffi, lib

from ._options import options
from .constants import (
    HeifBrand,
    HeifChannel,
    HeifChroma,
    HeifColorProfileType,
    HeifColorspace,
    HeifFiletype,
)
from .error import check_libheif_error


class HeifThumbnail:
    def __init__(self, *, size: tuple, has_alpha: bool, bit_depth: int, data, stride, **kwargs):
        self.size = size
        self.has_alpha = has_alpha
        self.mode = "RGBA" if has_alpha else "RGB"
        self.bit_depth = bit_depth
        self.data = data
        self.stride = stride
        self.img_id = kwargs["img_id"]

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with {str(len(self.data)) + ' bytes' if self.data else 'no'} data>"
        )

    def load(self):
        return self  # already loaded

    def close(self) -> None:
        self.data = None


class UndecodedHeifThumbnail(HeifThumbnail):
    def __init__(self, thumb_handle, *, transforms: bool, to_8bit: bool, **kwargs):
        self._handle = thumb_handle
        self.transforms = transforms
        self.to_8bit = to_8bit
        super().__init__(data=None, stride=None, **kwargs)

    def load(self):
        self.data, self.stride = _read_heif_image(self._handle, self)
        self.close()
        self.__class__ = HeifThumbnail
        return self

    def close(self) -> None:
        if hasattr(self, "_handle"):
            del self._handle


class HeifFile:
    def __init__(self, *, size: tuple, has_alpha: bool, bit_depth: int, data, stride, **kwargs):
        self.size = size
        self.has_alpha = has_alpha
        self.mode = "RGBA" if has_alpha else "RGB"
        self.bit_depth = bit_depth
        self.data = data
        self.stride = stride
        self.top_lvl_images = kwargs.get("top_lvl_images", [])
        self.thumbnails: List[Union[UndecodedHeifThumbnail, HeifThumbnail]] = kwargs["thumbnails"]
        self.info = {
            "main": kwargs["main"],
            "img_id": kwargs["img_id"],
            "brand": kwargs.get("brand", HeifBrand.UNKNOWN),
            "exif": kwargs.get("exif", None),
            "metadata": kwargs.get("metadata", []),
            "color_profile": kwargs.get("color_profile", {}),
        }
        if self.info["color_profile"]:
            if self.info["color_profile"]["type"] in ("rICC", "prof"):
                self.info["icc_profile"] = self.info["color_profile"]["data"]
            else:
                self.info["nclx_profile"] = self.info["color_profile"]["data"]

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with {str(len(self.data)) + ' bytes' if self.data else 'no'} image data "
            f"and {len(self.thumbnails)} thumbnails>"
        )

    def load(self):
        return self  # already loaded

    def close(self) -> None:
        for top_lvl_image in self.top_lvl_images:
            top_lvl_image.close()
        for thumbnail in self.thumbnails:
            thumbnail.close()
        self.data = None

    def __len__(self):
        return 1 + len(self.top_lvl_images)

    def __iter__(self):
        for i in range(len(self)):
            yield self if not i else self.top_lvl_images[i - 1]

    def __getitem__(self, index):
        if index < 0 or index > len(self.top_lvl_images):
            raise IndexError("invalid image index")
        return self if not index else self.top_lvl_images[index - 1]

    def thumbnails_all(self, one_for_image=False) -> Iterator[Union[UndecodedHeifThumbnail, HeifThumbnail]]:
        for i in self:
            for thumb in i.thumbnails:
                yield thumb
                if one_for_image:
                    break


class UndecodedHeifFile(HeifFile):
    def __init__(self, heif_handle, *, transforms: bool, to_8bit: bool, **kwargs):
        self._handle = heif_handle
        self.transforms = transforms
        self.to_8bit = to_8bit
        super().__init__(data=None, stride=None, **kwargs)

    def load(self):
        for top_lvl_image in self.top_lvl_images:
            top_lvl_image.load()
        for thumbnail in self.thumbnails:
            thumbnail.load()
        self.data, self.stride = _read_heif_image(self._handle, self)
        self.close()
        self.__class__ = HeifFile
        return self

    def close(self) -> None:
        for top_lvl_image in self.top_lvl_images:
            if top_lvl_image.__class__ == UndecodedHeifFile:
                top_lvl_image.close()
        for thumbnail in self.thumbnails:
            if thumbnail.__class__ == UndecodedHeifThumbnail:
                thumbnail.close()
        if hasattr(self, "_handle"):
            del self._handle


def check_heif(fp):
    """
    Wrapper around `libheif.heif_check_filetype`.

    Note: If `fp` contains less 12 bytes, then returns `HeifFiletype.NO`.

    :param fp: A filename (string), pathlib.Path object, file object or bytes.
       The file object must implement ``file.read``, ``file.seek`` and ``file.tell`` methods,
       and be opened in binary mode.
    :returns: `HeifFiletype`
    """
    magic = _get_bytes(fp, 16)
    return HeifFiletype.NO if len(magic) < 12 else lib.heif_check_filetype(magic, len(magic))


def is_supported(fp) -> bool:
    """
    Checks if `fp` contains a supported file type, by calling :py:func:`~pillow_heif.reader.check_heif` function.
    If `heif_filetype_yes_supported` or `heif_filetype_maybe` then returns True.
    If `heif_filetype_no` then returns False.
    OPTIONS
    "strict": `bool` determine what to return for `heif_filetype_yes_unsupported`.
    "avif": `bool` determine will be `avif` files marked as supported.
    If it is False from start, then pillow_heif was build without codecs for AVIF and you should not set it to true.
    """
    magic = _get_bytes(fp, 16)
    heif_filetype = check_heif(magic)
    if heif_filetype == HeifFiletype.NO or (not options().avif and magic[8:12] in (b"avif", b"avis")):
        return False
    if heif_filetype in (HeifFiletype.YES_SUPPORTED, HeifFiletype.MAYBE):
        return True
    return not options().strict


def get_file_mimetype(fp) -> str:
    """
    Wrapper around `libheif.get_file_mimetype`.

    :param fp: A filename (string), pathlib.Path object, file object or bytes.
       The file object must implement ``file.read``, ``file.seek`` and ``file.tell`` methods,
       and be opened in binary mode.
    :returns: string with `image/*`. If the format could not be detected, an empty string is returned.
    """
    __data = _get_bytes(fp, 50)
    return ffi.string(lib.heif_get_file_mime_type(__data, len(__data))).decode()


def open_heif(fp, *, apply_transformations: bool = True, convert_hdr_to_8bit: bool = True) -> UndecodedHeifFile:
    file_data = _get_bytes(fp)
    ctx = lib.heif_context_alloc()
    collect = _keep_refs(lib.heif_context_free, data=file_data)
    ctx = ffi.gc(ctx, collect, size=len(file_data))
    return _read_heif_context(ctx, file_data, apply_transformations, convert_hdr_to_8bit)


def read_heif(fp, *, apply_transformations: bool = True, convert_hdr_to_8bit: bool = True) -> HeifFile:
    heif_file = open_heif(
        fp,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
    )
    return heif_file.load()


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


def _keep_refs(destructor, **refs):
    """
    Keep refs to passed arguments until `inner` callback exist.
    This prevents collecting parent objects until all children are collected.
    """

    def inner(cdata):
        return destructor(cdata)

    inner._refs = refs
    return inner


def _read_heif_context(ctx, data, transforms: bool, to_8bit: bool) -> UndecodedHeifFile:
    brand = lib.heif_main_brand(data[:12], 12)
    error = lib.heif_context_read_from_memory_without_copy(ctx, data, len(data), ffi.NULL)
    check_libheif_error(error)
    p_main_id = ffi.new("heif_item_id *")
    error = lib.heif_context_get_primary_image_ID(ctx, p_main_id)
    check_libheif_error(error)
    p_main_handle = ffi.new("struct heif_image_handle **")
    error = lib.heif_context_get_primary_image_handle(ctx, p_main_handle)
    check_libheif_error(error)
    collect = _keep_refs(lib.heif_image_handle_release, ctx=ctx)
    handle = ffi.gc(p_main_handle[0], collect)
    return _read_heif_handle(ctx, p_main_id[0], handle, transforms, to_8bit, brand=brand, main=True)


def _read_heif_handle(ctx, img_id, handle, transforms: bool, to_8bit: bool, **kwargs) -> UndecodedHeifFile:
    _width = lib.heif_image_handle_get_width(handle)
    _height = lib.heif_image_handle_get_height(handle)
    _metadata = _read_metadata(handle)
    _exif = _retrieve_exif(_metadata)
    _color_profile = _read_color_profile(handle)
    _thumbnails = _read_thumbnails(ctx, handle, transforms, to_8bit)
    _images = _get_other_top_imgs(ctx, img_id, transforms, to_8bit, kwargs["brand"]) if kwargs["main"] else []
    return UndecodedHeifFile(
        handle,
        size=(_width, _height),
        has_alpha=bool(lib.heif_image_handle_has_alpha_channel(handle)),
        bit_depth=lib.heif_image_handle_get_luma_bits_per_pixel(handle),
        transforms=transforms,
        to_8bit=to_8bit,
        exif=_exif,
        metadata=_metadata,
        color_profile=_color_profile,
        thumbnails=_thumbnails,
        top_lvl_images=_images,
        img_id=img_id,
        **kwargs,
    )


def _read_metadata(handle) -> list:
    block_count = lib.heif_image_handle_get_number_of_metadata_blocks(handle, ffi.NULL)
    if block_count == 0:
        return []
    metadata = []
    blocks_ids = ffi.new("heif_item_id[]", block_count)
    lib.heif_image_handle_get_list_of_metadata_block_IDs(handle, ffi.NULL, blocks_ids, block_count)
    for block_id in blocks_ids:
        metadata_type = lib.heif_image_handle_get_metadata_type(handle, block_id)
        metadata_type = ffi.string(metadata_type).decode()
        data_length = lib.heif_image_handle_get_metadata_size(handle, block_id)
        if data_length > 0:
            p_data = ffi.new("char[]", data_length)
            error = lib.heif_image_handle_get_metadata(handle, block_id, p_data)
            check_libheif_error(error)
            data_buffer = ffi.buffer(p_data, data_length)
            data = bytes(data_buffer)
            if metadata_type == "Exif":
                data = data[4:]  # skip TIFF header, first 4 bytes
            metadata.append({"type": metadata_type, "data": data})
    return metadata


def _retrieve_exif(metadata: list):
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


def _get_chroma(hdr_to_8bit: bool, bit_depth: int, has_alpha: bool) -> HeifChroma:
    if hdr_to_8bit or bit_depth <= 8:
        chroma = HeifChroma.INTERLEAVED_RGBA if has_alpha else HeifChroma.INTERLEAVED_RGB
    else:
        if has_alpha:
            chroma = HeifChroma.INTERLEAVED_RRGGBBAA_BE
        else:
            chroma = HeifChroma.INTERLEAVED_RRGGBB_BE
    return chroma


def _read_heif_image(handle, heif_class: Union[UndecodedHeifFile, UndecodedHeifThumbnail]):
    colorspace = HeifColorspace.RGB
    chroma = _get_chroma(heif_class.to_8bit, heif_class.bit_depth, heif_class.has_alpha)
    p_options = lib.heif_decoding_options_alloc()
    p_options = ffi.gc(p_options, lib.heif_decoding_options_free)
    p_options.ignore_transformations = int(not heif_class.transforms)
    p_options.convert_hdr_to_8bit = int(heif_class.to_8bit)
    p_img = ffi.new("struct heif_image **")
    error = lib.heif_decode_image(handle, p_img, colorspace, chroma, p_options)
    check_libheif_error(error)
    img = p_img[0]
    p_stride = ffi.new("int *")
    p_data = lib.heif_image_get_plane_readonly(img, HeifChannel.INTERLEAVED, p_stride)
    stride = p_stride[0]
    data_length = heif_class.size[1] * stride
    # Release image as soon as no references to p_data left
    collect = partial(_release_heif_image, img)
    p_data = ffi.gc(p_data, collect, size=data_length)
    # ffi.buffer obligatory keeps a reference to p_data
    data_buffer = ffi.buffer(p_data, data_length)
    return data_buffer, stride


def _release_heif_image(img, _p_data=None) -> None:
    lib.heif_image_release(img)


def _read_thumbnails(ctx, handle, transforms: bool, to_8bit: bool) -> list:
    result: List[Union[UndecodedHeifThumbnail, HeifThumbnail]] = []
    if not options().thumbnails:
        return result
    thumbs_count = lib.heif_image_handle_get_number_of_thumbnails(handle)
    if thumbs_count == 0:
        return result
    thumbnails_ids = ffi.new("heif_item_id[]", thumbs_count)
    lib.heif_image_handle_get_list_of_thumbnail_IDs(handle, thumbnails_ids, thumbs_count)
    for thumbnail_id in thumbnails_ids:
        p_thumb_handle = ffi.new("struct heif_image_handle **")
        error = lib.heif_image_handle_get_thumbnail(handle, thumbnail_id, p_thumb_handle)
        check_libheif_error(error)
        collect = _keep_refs(lib.heif_image_handle_release, ctx=ctx)
        thumb_handle = ffi.gc(p_thumb_handle[0], collect)
        _thumbnail = _read_thumbnail_handle(thumb_handle, transforms, to_8bit, img_id=thumbnail_id)
        if options().thumbnails_autoload:
            _thumbnail.load()
        result.append(_thumbnail)
    return result


def _read_thumbnail_handle(handle, transforms: bool, to_8bit: bool, **kwargs) -> UndecodedHeifThumbnail:
    _width = lib.heif_image_handle_get_width(handle)
    _height = lib.heif_image_handle_get_height(handle)
    return UndecodedHeifThumbnail(
        handle,
        size=(_width, _height),
        has_alpha=bool(lib.heif_image_handle_has_alpha_channel(handle)),
        bit_depth=lib.heif_image_handle_get_luma_bits_per_pixel(handle),
        transforms=transforms,
        to_8bit=to_8bit,
        **kwargs,
    )


def _get_other_top_imgs(ctx, main_id, transforms: bool, to_8bit: bool, brand: HeifBrand) -> list:
    _result: List[UndecodedHeifFile] = []
    top_img_count = lib.heif_context_get_number_of_top_level_images(ctx)
    if not top_img_count > 1:
        return _result
    top_lvl_image_ids = ffi.new("heif_item_id[]", top_img_count)
    lib.heif_context_get_list_of_top_level_image_IDs(ctx, top_lvl_image_ids, top_img_count)
    for _image_id in top_lvl_image_ids:
        if _image_id == main_id:
            continue
        p_handle = ffi.new("struct heif_image_handle **")
        error = lib.heif_context_get_image_handle(ctx, _image_id, p_handle)
        check_libheif_error(error)
        collect = _keep_refs(lib.heif_image_handle_release, ctx=ctx)
        handle = ffi.gc(p_handle[0], collect)
        _image = _read_heif_handle(ctx, _image_id, handle, transforms, to_8bit, brand=brand, main=False)
        _result.append(_image)
    return _result


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
