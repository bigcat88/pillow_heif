"""
Callback functions and classes for libheif `heif_context_read_from_reader` and `heif_context_write`.
"""

import builtins
from io import SEEK_END, SEEK_SET, BytesIO
from pathlib import Path

from _pillow_heif_cffi import ffi, lib

from .misc import _get_bytes


class LibHeifCtx:
    def __init__(self, fp, transforms, to_8bit):
        self._fp_close_after = False
        self.fp = self._get_fp(fp)
        self.fp.seek(0, SEEK_SET)
        self.c_userdata = ffi.new_handle(self.fp)
        self.ctx = ffi.gc(lib.heif_context_alloc(), lib.heif_context_free)
        self.reader = self._get_libheif_reader()
        self.misc = {"transforms": transforms, "to_8bit": to_8bit, "brand": lib.heif_main_brand(_get_bytes(fp, 12), 12)}

    def __del__(self):
        if self._fp_close_after and self.fp and hasattr(self.fp, "close"):
            self.fp.close()
        self.fp = None

    def _get_fp(self, fp):
        if hasattr(fp, "read") and hasattr(fp, "tell") and hasattr(fp, "seek"):
            return fp
        self._fp_close_after = True
        if isinstance(fp, (str, Path)):
            return builtins.open(fp, "rb")
        return BytesIO(fp)

    @staticmethod
    def _get_libheif_reader():
        libheif_reader = ffi.new("struct heif_reader *")
        libheif_reader.reader_api_version = 1
        libheif_reader.get_position = lib.callback_tell
        libheif_reader.read = lib.callback_read
        libheif_reader.seek = lib.callback_seek
        libheif_reader.wait_for_file_size = lib.callback_wait_for_file_size
        return libheif_reader


class LibHeifCtxWrite:
    def __init__(self, fp):
        self._fp_close_after = False
        self.fp = self._get_fp(fp)
        self.c_userdata = ffi.new_handle(self.fp)
        self.ctx = ffi.gc(lib.heif_context_alloc(), lib.heif_context_free)
        self.writer = self._get_heif_writer()

    def __del__(self):
        if self._fp_close_after and self.fp and hasattr(self.fp, "close"):
            self.fp.close()
        self.fp = None

    def _get_fp(self, fp):
        if isinstance(fp, (str, Path)):
            self._fp_close_after = True
            return builtins.open(fp, "wb")
        if hasattr(fp, "write"):
            return fp
        raise TypeError("`fp` must be a path to file or and object with `write` method.")

    @staticmethod
    def _get_heif_writer():
        heif_writer = ffi.new("struct heif_writer *")
        heif_writer.writer_api_version = 1
        heif_writer.write = lib.callback_write
        return heif_writer


@ffi.def_extern()
def callback_tell(userdata):
    fp = ffi.from_handle(userdata)
    return fp.tell() if fp and not fp.closed else 0


@ffi.def_extern()
def callback_seek(position, userdata):
    fp = ffi.from_handle(userdata)
    if fp and not fp.closed:
        fp.seek(position)
    return 0


@ffi.def_extern()
def callback_read(data, size, userdata):
    fp = ffi.from_handle(userdata)
    if fp and not fp.closed:
        read_data = fp.read(size)
        ffi.memmove(data, read_data, len(read_data))
    return 0


@ffi.def_extern()
def callback_write(_ctx, data, size, userdata):
    fp = ffi.from_handle(userdata)
    if fp and not fp.closed:
        fp.write(ffi.buffer(data, size=size))
    return [0, 0, ffi.NULL]


@ffi.def_extern()
def callback_wait_for_file_size(target_size, userdata):
    fp = ffi.from_handle(userdata)
    fp_size = 0
    if fp and not fp.closed:
        fp_current = fp.tell()
        fp_size = fp.seek(0, SEEK_END)
        fp.seek(fp_current, SEEK_SET)
    return 2 if target_size > fp_size else 0
