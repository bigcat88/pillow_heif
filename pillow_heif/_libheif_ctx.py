"""
Callback functions and wrappers for libheif `heif_context_read_from_memory_without_copy` and `heif_context_write`.
"""

import builtins
from io import SEEK_SET
from pathlib import Path
from typing import Dict, List

from _pillow_heif_cffi import ffi, lib

from .constants import HeifCompressionFormat
from .error import check_libheif_error
from .misc import _get_bytes, get_file_mimetype


def _get_heif_writer():
    heif_writer = ffi.new("struct heif_writer *")
    heif_writer.writer_api_version = 1
    heif_writer.write = lib.callback_write
    return heif_writer


HEIF_WRITER = _get_heif_writer()


class LibHeifCtx:
    """LibHeif reader context"""

    def __init__(self, fp, to_8bit: bool = False):
        self.to_8bit = to_8bit
        self.ctx = ffi.gc(lib.heif_context_alloc(), lib.heif_context_free)
        if hasattr(fp, "seek"):
            fp.seek(0, SEEK_SET)
        self.c_userdata = bytes(_get_bytes(fp))
        cdata_buf = ffi.from_buffer(self.c_userdata)  # For PyPy3, without this it will raise error during read.
        error = lib.heif_context_read_from_memory_without_copy(self.ctx, cdata_buf, len(cdata_buf), ffi.NULL)
        check_libheif_error(error)
        self.mimetype = get_file_mimetype(self.c_userdata)

    def get_main_img_id(self) -> int:
        p_main_image_id = ffi.new("heif_item_id *")
        check_libheif_error(lib.heif_context_get_primary_image_ID(self.ctx, p_main_image_id))
        return p_main_image_id[0]

    def get_top_images_ids(self) -> List[int]:
        top_img_count = lib.heif_context_get_number_of_top_level_images(self.ctx)
        top_img_ids = ffi.new("heif_item_id[]", top_img_count)
        top_img_count = lib.heif_context_get_list_of_top_level_image_IDs(self.ctx, top_img_ids, top_img_count)
        return [top_img_ids[i] for i in range(top_img_count)]


class LibHeifCtxWrite:
    """LibHeif writer context"""

    def __init__(self, compression_format: int = HeifCompressionFormat.HEVC):
        self.ctx = ffi.gc(lib.heif_context_alloc(), lib.heif_context_free)
        p_encoder = ffi.new("struct heif_encoder **")
        error = lib.heif_context_get_encoder_for_format(self.ctx, compression_format, p_encoder)
        check_libheif_error(error)
        self.encoder = ffi.gc(p_encoder[0], lib.heif_encoder_release)
        # lib.heif_encoder_set_logging_level(self.encoder, 4)

    def set_encoder_parameters(self, enc_params: Dict[str, str], quality: int = None):
        if quality is not None:
            if quality == -1:
                check_libheif_error(lib.heif_encoder_set_lossless(self.encoder, True))
            else:
                check_libheif_error(lib.heif_encoder_set_lossy_quality(self.encoder, quality))
        for key, value in enc_params.items():
            _value = value if isinstance(value, str) else str(value)
            check_libheif_error(
                lib.heif_encoder_set_parameter(self.encoder, key.encode("ascii"), _value.encode("ascii"))
            )

    def write(self, fp):
        __fp = self._get_fp(fp)
        c_userdata = ffi.new_handle(__fp)
        error = lib.heif_context_write(self.ctx, HEIF_WRITER, c_userdata)
        if isinstance(fp, (str, Path)):
            __fp.close()
        check_libheif_error(error)

    @staticmethod
    def _get_fp(fp):
        if isinstance(fp, (str, Path)):
            return builtins.open(fp, "wb")
        if hasattr(fp, "write"):
            return fp
        raise TypeError("`fp` must be a path to file or an object with `write` method.")


@ffi.def_extern()
def callback_write(_ctx, data, size, userdata):
    fp = ffi.from_handle(userdata)
    fp.write(ffi.buffer(data, size=size))
    return [0, 0, ffi.NULL]
