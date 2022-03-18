"""
Exceptions that can be raised during library calls.
"""

from _pillow_heif_cffi import ffi

from .constants import HeifErrorCode


class HeifError(ValueError):
    def __init__(self, *, code, subcode, message):
        super().__init__(code, subcode, message)
        self.code = code
        self.subcode = subcode
        self.message = message

    def __str__(self):
        return f"Code: {self.code}, Subcode: {self.subcode}, Message: `{self.message}`"

    def __repr__(self):
        return f"{repr(HeifErrorCode(self.code))}, {self.subcode}, {self.message}"


def check_libheif_error(error_struct):
    """
    Helper function. Checks returned result error_struct from libheif calls and raise exception if error.
    """

    if error_struct.code == HeifErrorCode.OK:
        return
    raise HeifError(
        code=error_struct.code,
        subcode=error_struct.subcode,
        message=ffi.string(error_struct.message).decode(),
    )
