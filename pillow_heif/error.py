"""
Custom exception that can be raised during library calls.
"""

from _pillow_heif_cffi import ffi

from .constants import HeifErrorCode


class HeifError(ValueError):
    """
    Raised in :py:meth:`pillow_heif.open_heif` if an image cannot be opened or corrupted.

    Also can be raised during image decoding or during saving.
    """

    def __init__(self, *, code, subcode, message):
        super().__init__(code, subcode, message)
        self.code = code
        self.subcode = subcode
        self.message = message

    def __str__(self):
        return f"Code: {self.code}, Subcode: {self.subcode}, Message: `{self.message}`"

    def __repr__(self):
        return f"{repr(HeifErrorCode(self.code))}, {self.subcode}, {self.message}"


def check_libheif_error(error_struct) -> None:
    """
    Helper function. Checks returned result error_struct from libheif calls and raise exception if error.

    :param error_struct: ``heif_error`` struct from libheif.

    :exception HeifError: If there is an error code.
    """

    if error_struct.code == HeifErrorCode.OK:
        return
    raise HeifError(
        code=error_struct.code,
        subcode=error_struct.subcode,
        message=ffi.string(error_struct.message).decode(),
    )
