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
        self.fp_size = self.fp.seek(0, SEEK_END)
        self.fp.seek(0, SEEK_SET)
        self.ctx = ffi.gc(lib.heif_context_alloc(), lib.heif_context_free)
        self.reader = self._get_libheif_reader()
        self.cpointer = ffi.new_handle(self)
        self.misc = {"transforms": transforms, "to_8bit": to_8bit, "brand": lib.heif_main_brand(_get_bytes(fp, 12), 12)}

    def __del__(self):
        self.close()
        self.cpointer = None

    def tell(self):
        return self.fp.tell()

    def seek(self, position):
        if self.fp is None:
            return 0
        self.fp.seek(position)
        return 0

    def read(self, data, size):
        if self.fp is None:
            return 0
        read_data = self.fp.read(size)
        ffi.memmove(data, read_data, len(read_data))
        return 0

    def wait_for_file_size(self, target_size):
        return 2 if target_size > self.fp_size and self.fp else 0

    def close(self):
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
        self.ctx = ffi.gc(lib.heif_context_alloc(), lib.heif_context_free)
        self.writer = self._get_heif_writer()
        self.cpointer = ffi.new_handle(self)
        self._error_message = ffi.new("char*")

    def __del__(self):
        self.close()
        self.cpointer = None

    def write(self, data, size):
        self.fp.write(ffi.buffer(data, size=size))
        return [0, 0, self._error_message]

    def close(self):
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
    return ffi.from_handle(userdata).tell()


@ffi.def_extern()
def callback_seek(position, userdata):
    return ffi.from_handle(userdata).seek(position)


@ffi.def_extern()
def callback_read(data, size, userdata):
    return ffi.from_handle(userdata).read(data, size)


@ffi.def_extern()
def callback_write(_ctx, data, size, userdata):
    return ffi.from_handle(userdata).write(data, size)


@ffi.def_extern()
def callback_wait_for_file_size(target_size, userdata):
    return ffi.from_handle(userdata).wait_for_file_size(target_size)
