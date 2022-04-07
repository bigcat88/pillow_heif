"""
Functions and classes for heif images to read and write.
"""
import builtins
from typing import Any, Dict, Iterator, List, Tuple, Union
from warnings import warn

from _pillow_heif_cffi import ffi, lib
from PIL import Image, ImageSequence

from ._libheif_ctx import LibHeifCtx, LibHeifCtxWrite
from ._options import options
from .constants import (
    HeifBrand,
    HeifChannel,
    HeifChroma,
    HeifColorProfileType,
    HeifColorspace,
    HeifCompressionFormat,
    HeifFiletype,
    HeifSaveMask,
)
from .error import HeifError, HeifErrorCode, check_libheif_error
from .misc import _get_bytes, _get_chroma


class HeifImageBase:
    def __init__(self, heif_ctx: Union[LibHeifCtx, dict], handle):
        self._img_data: Dict[str, Any] = {}
        if isinstance(heif_ctx, LibHeifCtx):
            self.misc = {
                "transforms": heif_ctx.misc["transforms"],
                "to_8bit": heif_ctx.misc["to_8bit"],
            }
            self._handle = ffi.gc(handle, lib.heif_image_handle_release)
            self.size = (
                lib.heif_image_handle_get_width(self._handle),
                lib.heif_image_handle_get_height(self._handle),
            )
            self.bit_depth = lib.heif_image_handle_get_luma_bits_per_pixel(self._handle)
            self.has_alpha = bool(lib.heif_image_handle_has_alpha_channel(self._handle))
        else:
            self._handle = None
            self.bit_depth = heif_ctx["bit_depth"]
            self.size = heif_ctx["size"]
            self.has_alpha = heif_ctx["mode"] == "RGBA"
            if self.bit_depth == 8:
                _chroma = HeifChroma.INTERLEAVED_RGBA if self.has_alpha else HeifChroma.INTERLEAVED_RGB
            else:
                _chroma = HeifChroma.INTERLEAVED_RRGGBBAA_BE if self.has_alpha else HeifChroma.INTERLEAVED_RRGGBB_BE
            _stride = heif_ctx.get("stride", None)
            _img = _create_image(
                self.size, HeifColorspace.RGB, _chroma, self.bit_depth, heif_ctx["mode"], heif_ctx["data"], _stride
            )
            self._img_to_img_data_dict(_img, HeifColorspace.RGB, _chroma)

    @property
    def mode(self) -> str:
        return "RGBA" if self.has_alpha else "RGB"

    @property
    def heif_img(self):
        self._load_if_not()
        return self._img_data.get("img", None)

    @property
    def data(self):
        self._load_if_not()
        return self._img_data.get("data", None)

    @property
    def stride(self):
        self._load_if_not()
        return self._img_data.get("stride", None)

    @property
    def chroma(self):
        return self._img_data.get("chroma", HeifChroma.UNDEFINED)

    @property
    def color(self):
        return self._img_data.get("color", HeifColorspace.UNDEFINED)

    def _load_if_not(self):
        if self._img_data or self._handle is None:
            return
        colorspace = HeifColorspace.RGB
        chroma = _get_chroma(self.misc["to_8bit"], self.bit_depth, self.has_alpha)
        p_options = lib.heif_decoding_options_alloc()
        p_options = ffi.gc(p_options, lib.heif_decoding_options_free)
        p_options.ignore_transformations = int(not self.misc["transforms"])
        p_options.convert_hdr_to_8bit = int(self.misc["to_8bit"])
        p_img = ffi.new("struct heif_image **")
        check_libheif_error(lib.heif_decode_image(self._handle, p_img, colorspace, chroma, p_options))
        heif_img = ffi.gc(p_img[0], lib.heif_image_release)
        self._img_to_img_data_dict(heif_img, colorspace, chroma)

    def _img_to_img_data_dict(self, heif_img, colorspace, chroma):
        p_stride = ffi.new("int *")
        p_data = lib.heif_image_get_plane(heif_img, HeifChannel.INTERLEAVED, p_stride)
        stride = p_stride[0]
        data_length = self.size[1] * stride
        data_buffer = ffi.buffer(p_data, data_length)
        self._img_data.update(img=heif_img, data=data_buffer, stride=stride, color=colorspace, chroma=chroma)

    def load(self):
        self._load_if_not()
        return self

    def unload(self):
        self._img_data.clear()

    def close(self):
        self.unload()
        self._handle = None


class HeifThumbnail(HeifImageBase):
    def __init__(self, heif_ctx: Union[LibHeifCtx, dict], img_handle, thumb_id: int, img_index: int):
        if isinstance(heif_ctx, LibHeifCtx):
            p_handle = ffi.new("struct heif_image_handle **")
            check_libheif_error(lib.heif_image_handle_get_thumbnail(img_handle, thumb_id, p_handle))
            handle = p_handle[0]
        else:
            handle = None
        super().__init__(heif_ctx, handle)
        self.info = {
            "thumb_id": thumb_id,
            "img_index": img_index,
        }

    def __repr__(self):
        _bytes = f"{len(self.data)} bytes" if self._img_data else "no"
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with id = {self.info['thumb_id']} for img with index = {self.info['img_index']} "
            f"and with {_bytes} image data>"
        )


class HeifImage(HeifImageBase):
    def __init__(self, img_id: int, img_index: int, heif_ctx: Union[LibHeifCtx, dict]):
        additional_info = {}
        if isinstance(heif_ctx, LibHeifCtx):
            brand = heif_ctx.misc["brand"]
            p_handle = ffi.new("struct heif_image_handle **")
            error = lib.heif_context_get_image_handle(heif_ctx.ctx, img_id, p_handle)
            if error.code != HeifErrorCode.OK and not img_index:
                error = lib.heif_context_get_primary_image_handle(heif_ctx.ctx, p_handle)
            check_libheif_error(error)
            handle = p_handle[0]
            _metadata = _read_metadata(handle)
            _exif = _retrieve_exif(_metadata)
            additional_info["metadata"] = _metadata
            _color_profile = _read_color_profile(handle)
            if _color_profile:
                if _color_profile["type"] in ("rICC", "prof"):
                    additional_info["icc_profile"] = _color_profile["data"]
                    additional_info["icc_profile_type"] = _color_profile["type"]
                else:
                    additional_info["nclx_profile"] = _color_profile["data"]
        else:
            brand = HeifBrand.UNKNOWN
            handle = None
            _exif = None
            additional_info["metadata"] = []
            additional_info.update(heif_ctx.get("additional_info", {}))
        super().__init__(heif_ctx, handle)
        self.info = {
            "main": not img_index,
            "img_id": img_id,
            "brand": brand,
            "exif": _exif,
        }
        self.info.update(**additional_info)
        self.thumbnails = _read_thumbnails(heif_ctx, self._handle, img_index)

    def __repr__(self):
        _bytes = f"{len(self.data)} bytes" if self._img_data else "no"
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with id = {self.info['img_id']}, {len(self.thumbnails)} thumbnails "
            f"and with {_bytes} image data>"
        )

    def load(self):
        super().load()
        for thumbnail in self.thumbnails:
            thumbnail.load()
        return self

    def unload(self):
        super().unload()
        for thumbnail in self.thumbnails:
            thumbnail.unload()
        return self

    def scale(self, width: int, height: int):
        self._load_if_not()
        p_scaled_img = ffi.new("struct heif_image **")
        check_libheif_error(lib.heif_image_scale_image(self.heif_img, p_scaled_img, width, height, ffi.NULL))
        scaled_heif_img = ffi.gc(p_scaled_img[0], lib.heif_image_release)
        self.size = (
            lib.heif_image_get_primary_width(scaled_heif_img),
            lib.heif_image_get_primary_height(scaled_heif_img),
        )
        self._img_to_img_data_dict(scaled_heif_img, self.color, self.chroma)
        return self


class HeifFile:
    def __init__(self, heif_ctx: Union[LibHeifCtx, dict], img_ids: list = None):
        self._images: List[HeifImage] = []
        self._heif_ctx: Union[LibHeifCtx, dict, None] = heif_ctx
        if img_ids:
            for i, img_id in enumerate(img_ids):
                self._images.append(HeifImage(img_id, i, heif_ctx))

    @property
    def size(self):
        return self._images[0].size

    @property
    def mode(self):
        return self._images[0].mode

    @property
    def data(self):
        return self._images[0].data

    @property
    def stride(self):
        return self._images[0].stride

    @property
    def chroma(self):
        return self._images[0].chroma

    @property
    def color(self):
        return self._images[0].color

    @property
    def has_alpha(self):
        return self._images[0].has_alpha

    @property
    def bit_depth(self):
        return self._images[0].bit_depth

    @property
    def info(self):
        return self._images[0].info

    @property
    def thumbnails(self):
        return self._images[0].thumbnails

    def thumbnails_all(self, one_for_image=False) -> Iterator[HeifThumbnail]:
        for i in self:
            for thumb in i.thumbnails:
                yield thumb
                if one_for_image:
                    break

    def load(self, everything: bool = False):
        if everything:
            for img in self:
                img.load()
        else:
            self._images[0].load()
        return self

    def unload(self, everything: bool = False):
        if everything:
            for img in self:
                img.unload()
        else:
            self._images[0].unload()
        return self

    def scale(self, width: int, height: int) -> None:
        self._images[0].scale(width, height)

    def add_frombytes(self, bit_depth: int, mode: str, size: tuple, data, **kwargs):
        __ids = [i.info["img_id"] for i in self._images] + [i.info["thumb_id"] for i in self.thumbnails_all()] + [0]
        __new_id = 2 + max(__ids)
        __heif_ctx = self.__heif_ctx_as_dict(bit_depth, mode, size, data, **kwargs)
        self._images.append(HeifImage(__new_id, len(self), __heif_ctx))
        return self

    # def append_image(self):
    #     pass

    def add_from_pillow(self, pil_image: Image, load_one=False):
        for frame in ImageSequence.Iterator(pil_image):
            additional_info = {}
            for k in ("exif", "icc_profile", "icc_profile_type", "nclx_profile", "metadata", "brand"):
                if k in frame.info:
                    additional_info[k] = frame.info[k]
            if frame.mode == "P":
                frame = frame.convert(mode="RGB")
            # How here we can detect bit depth of Pillow image? pallete.rawmode or maybe something else?
            __bit_depth = 8
            self.add_frombytes(__bit_depth, frame.mode, frame.size, frame.tobytes(), add_info={**additional_info})
            if load_one:
                break
        return self

    def add_from_heif(self, heif_image):
        if isinstance(heif_image, HeifFile):
            heif_images = [i for i in heif_image]
        else:
            heif_images = [heif_image]
        for image in heif_images:
            additional_info = image.info.copy()
            additional_info.pop("img_id", None)
            additional_info.pop("main", None)
            self.add_frombytes(
                image.bit_depth,
                image.mode,
                image.size,
                image.data,
                stride=image.stride,
                add_info={**additional_info},
            )
            for thumb in image.thumbnails:
                self._images[len(self._images) - 1].thumbnails.append(
                    self.__get_image_thumb_frombytes(
                        thumb.bit_depth,
                        thumb.mode,
                        thumb.size,
                        thumb.data,
                        img_index=len(self._images),
                        stride=thumb.stride,
                    )
                )

    def get_img_thumb_mask_for_save(self, mask=HeifSaveMask.SAVE_ALL, thumb_box: int = 0) -> list:
        if mask == HeifSaveMask.SAVE_ALL:
            return [[True, [thumb_box if thumb_box else max(_.size) for _ in img.thumbnails]] for img in self._images]
        result = [[False, [thumb_box if thumb_box else max(_.size) for _ in img.thumbnails]] for img in self._images]
        if mask == HeifSaveMask.SAVE_ONE:
            result[0][0] = True
        return result

    @staticmethod
    def add_thumbs_to_mask(save_mask: list, thumb_boxes: list) -> None:
        for i in range(len(save_mask)):
            save_mask[i][1].extend([_ for _ in thumb_boxes if _ not in save_mask[i][1]])

    def save(self, fp, save_mask: list = None, **kwargs):
        # append_images = kwargs.get("append_images", [])
        if not options().hevc_enc:
            raise HeifError(code=HeifErrorCode.ENCODING_ERROR, subcode=5000, message="No encoder found.")
        _save_mask = save_mask if save_mask else self.get_img_thumb_mask_for_save()
        quality = kwargs.get("quality", None)
        enc_params = kwargs.get("enc_params", [])
        _heif_write_ctx = LibHeifCtxWrite(fp)
        _encoder = self._get_encoder(_heif_write_ctx, quality, enc_params)
        self._save(_heif_write_ctx, _encoder, _save_mask)
        error = lib.heif_context_write(_heif_write_ctx.ctx, _heif_write_ctx.writer, _heif_write_ctx.cpointer)
        check_libheif_error(error)
        _heif_write_ctx.close()

    def close(self, only_fp: bool = False, thumbnails: bool = True):
        if isinstance(self._heif_ctx, LibHeifCtx):
            self._heif_ctx.close()
        if not only_fp:
            for img in self:
                if thumbnails:
                    for thumb in img.thumbnails:
                        thumb.close()
                img.close()
            self._heif_ctx = None

    def __repr__(self):
        return f"<{self.__class__.__name__} with {len(self)} images: {[str(i) for i in self]}>"

    def __len__(self):
        return len(self._images)

    def __iter__(self):
        for _ in self._images:
            yield _

    def __getitem__(self, index):
        if index < 0 or index >= len(self._images):
            raise IndexError(f"invalid image index: {index}")
        return self._images[index]

    def __del__(self):
        self.close()

    def _save(self, out_ctx: LibHeifCtxWrite, encoder, save_mask: list):
        encoding_options = lib.heif_encoding_options_alloc()
        encoding_options = ffi.gc(encoding_options, lib.heif_encoding_options_free)
        for i, img in enumerate(self):
            if not save_mask[i][0]:
                continue
            img.load()
            # new_img = img.heif_img
            __bit_depth = 8 if getattr(img, "misc", {}).get("to_8bit", None) else img.bit_depth
            new_img = _create_image(
                img.size, HeifColorspace.RGB, img.chroma, __bit_depth, img.mode, img.data, img.stride
            )
            __icc_profile = img.info.get("icc_profile", None)
            if __icc_profile is not None:
                _prof_type = img.info.get("icc_profile_type", "prof").encode("ascii")
                error = lib.heif_image_set_raw_color_profile(
                    new_img, _prof_type, img.info["icc_profile"], len(img.info["icc_profile"])
                )
                check_libheif_error(error)
            elif img.info.get("nclx_profile", None):
                error = lib.heif_image_set_nclx_color_profile(
                    new_img,
                    ffi.cast("const struct heif_color_profile_nclx*", ffi.from_buffer(img.info["nclx_profile"])),
                )
                check_libheif_error(error)
            p_new_img_handle = ffi.new("struct heif_image_handle **")
            error = lib.heif_context_encode_image(out_ctx.ctx, new_img, encoder, encoding_options, p_new_img_handle)
            check_libheif_error(error)
            new_img_handle = ffi.gc(p_new_img_handle[0], lib.heif_image_handle_release)
            if img.info["exif"] is not None:
                error = lib.heif_context_add_exif_metadata(
                    out_ctx.ctx, new_img_handle, img.info["exif"], len(img.info["exif"])
                )
                check_libheif_error(error)
            for metadata in img.info["metadata"]:
                error = lib.heif_context_add_generic_metadata(
                    out_ctx.ctx,
                    new_img_handle,
                    metadata["data"],
                    len(metadata["data"]),
                    metadata["metadata_type"],
                    metadata["content_type"],
                )
                check_libheif_error(error)
            thumbs_masks = save_mask[i][1]
            for thumb_i, thumb_box in enumerate(thumbs_masks):
                if thumb_box:
                    if max(img.size) > thumb_box > 3:
                        p_new_thumb_handle = ffi.new("struct heif_image_handle **")
                        error = lib.heif_context_encode_thumbnail(
                            out_ctx.ctx,
                            new_img,
                            new_img_handle,
                            encoder,
                            encoding_options,
                            thumb_box,
                            p_new_thumb_handle,
                        )
                        check_libheif_error(error)
                        if p_new_thumb_handle[0] != ffi.NULL:
                            lib.heif_image_handle_release(p_new_thumb_handle[0])

    @staticmethod
    def _get_encoder(heif_ctx, quality: int = None, enc_params: List[Tuple[str, str]] = None):
        p_encoder_descriptor = ffi.new("struct heif_encoder_descriptor **")
        lib.heif_context_get_encoder_descriptors(
            heif_ctx.cpointer, HeifCompressionFormat.HEVC, ffi.NULL, p_encoder_descriptor, 1
        )
        p_encoder = ffi.new("struct heif_encoder **")
        error = lib.heif_context_get_encoder(heif_ctx.cpointer, p_encoder_descriptor[0], p_encoder)
        check_libheif_error(error)
        encoder = ffi.gc(p_encoder[0], lib.heif_encoder_release)
        # lib.heif_encoder_set_logging_level(encoder, 4)
        if quality is None and options().quality is not None:
            quality = options().quality
        if quality:
            lib.heif_encoder_set_lossy_quality(encoder, quality)
        if enc_params:
            for enc_param in enc_params:
                check_libheif_error(
                    lib.heif_encoder_set_parameter(encoder, enc_param[0].encode("ascii"), enc_param[1].encode("ascii"))
                )
        return encoder

    def __get_image_thumb_frombytes(self, bit_depth: int, mode: str, size: tuple, data, img_index: int, **kwargs):
        __ids = [i.info["img_id"] for i in self._images] + [i.info["thumb_id"] for i in self.thumbnails_all()] + [0]
        __new_id = 2 + max(__ids)
        __heif_ctx = self.__heif_ctx_as_dict(bit_depth, mode, size, data, **kwargs)
        return HeifThumbnail(__heif_ctx, None, __new_id, img_index)

    @staticmethod
    def __heif_ctx_as_dict(bit_depth: int, mode: str, size: tuple, data, **kwargs) -> dict:
        __factor = 1 if bit_depth == 8 else 2
        __bytes_per_pix = 3 * __factor if mode == "RGB" else 4 * __factor
        __stride = kwargs.get("stride", None)
        return {
            "bit_depth": bit_depth,
            "mode": mode,
            "size": size,
            "data": data,
            "stride": __stride if __stride else size[0] * __bytes_per_pix,
            "additional_info": kwargs.get("add_info", {}),
        }

    def debug_dump(self, file_path="debug_boxes_dump.txt"):
        with builtins.open(file_path, "wb") as f:
            lib.heif_context_debug_dump_boxes_to_file(self._heif_ctx.ctx, f.fileno())


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


def open_heif(fp, apply_transformations: bool = True, convert_hdr_to_8bit: bool = True) -> HeifFile:
    heif_ctx = LibHeifCtx(fp, apply_transformations, convert_hdr_to_8bit)
    check_libheif_error(lib.heif_context_read_from_reader(heif_ctx.ctx, heif_ctx.reader, heif_ctx.cpointer, ffi.NULL))
    p_main_image_id = ffi.new("heif_item_id *")
    check_libheif_error(lib.heif_context_get_primary_image_ID(heif_ctx.ctx, p_main_image_id))
    main_image_id = p_main_image_id[0]
    top_img_count = lib.heif_context_get_number_of_top_level_images(heif_ctx.ctx)
    top_img_ids = ffi.new("heif_item_id[]", top_img_count)
    top_img_count = lib.heif_context_get_list_of_top_level_image_IDs(heif_ctx.ctx, top_img_ids, top_img_count)
    img_list = [main_image_id]
    for i in range(top_img_count):
        if top_img_ids[i] != main_image_id:
            img_list.append(top_img_ids[i])
    return HeifFile(heif_ctx, img_list)


def from_pillow(pil_image: Image, load_one=False) -> HeifFile:
    return HeifFile({}).add_from_pillow(pil_image, load_one)


def _read_metadata(handle) -> list:
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


def _read_thumbnails(heif_ctx: Union[LibHeifCtx, dict], img_handle, img_index: int) -> List[HeifThumbnail]:
    result: List[HeifThumbnail] = []
    if img_handle is None or not options().thumbnails:
        return result
    thumbs_count = lib.heif_image_handle_get_number_of_thumbnails(img_handle)
    if thumbs_count == 0:
        return result
    thumbnails_ids = ffi.new("heif_item_id[]", thumbs_count)
    thumb_count = lib.heif_image_handle_get_list_of_thumbnail_IDs(img_handle, thumbnails_ids, thumbs_count)
    for i in range(thumb_count):
        result.append(HeifThumbnail(heif_ctx, img_handle, thumbnails_ids[i], img_index))
    return result


def _create_image(
    size: tuple, color: HeifColorspace, chroma: HeifChroma, bit_depth: int, mode: str, data, stride: int = None
):
    width, height = size
    p_new_img = ffi.new("struct heif_image **")
    error = lib.heif_image_create(width, height, color, chroma, p_new_img)
    check_libheif_error(error)
    new_img = ffi.gc(p_new_img[0], lib.heif_image_release)
    error = lib.heif_image_add_plane(new_img, HeifChannel.INTERLEAVED, width, height, bit_depth)
    check_libheif_error(error)
    p_dest_stride = ffi.new("int *")
    p_data = lib.heif_image_get_plane(new_img, HeifChannel.INTERLEAVED, p_dest_stride)
    dest_stride = p_dest_stride[0]
    p_source = ffi.from_buffer("uint8_t*", data)
    __factor = 1 if bit_depth == 8 else 2
    source_stride = stride if stride else width * 3 * __factor if mode == "RGB" else width * 4 * __factor
    if dest_stride == source_stride:
        ffi.memmove(p_data, data, len(data))
    else:
        for i in range(height):
            ffi.memmove(p_data + dest_stride * i, p_source + source_stride * i, source_stride)
    return new_img


# --------------------------------------------------------------------
# DEPRECATED FUNCTIONS.


def check(fp):
    warn("Function `check` is deprecated, use `check_heif` instead.", DeprecationWarning)
    return check_heif(fp)  # pragma: no cover


def open(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):  # pylint: disable=redefined-builtin
    warn("Function `open` is deprecated and will be removed in 0.2.1, use `open_heif` instead.", DeprecationWarning)
    return open_heif(
        fp, apply_transformations=apply_transformations, convert_hdr_to_8bit=convert_hdr_to_8bit
    )  # pragma: no cover


def read(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):
    warn("Function `read` is deprecated, use `open_heif` instead.", DeprecationWarning)
    return open_heif(
        fp, apply_transformations=apply_transformations, convert_hdr_to_8bit=convert_hdr_to_8bit
    )  # pragma: no cover


def read_heif(fp, *, apply_transformations: bool = True, convert_hdr_to_8bit: bool = True) -> HeifFile:
    warn("Function `read_heif` is deprecated, use `open_heif` instead. Read docs, why.", DeprecationWarning)
    return open_heif(
        fp,
        apply_transformations=apply_transformations,
        convert_hdr_to_8bit=convert_hdr_to_8bit,
    )  # pragma: no cover
