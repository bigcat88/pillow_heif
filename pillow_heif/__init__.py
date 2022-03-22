"""
Import all possible stuff that can be used.
"""


from ._lib_info import (
    have_decoder_for_format,
    have_encoder_for_format,
    libheif_info,
    libheif_version,
)
from ._options import options
from ._version import __version__
from .as_opener import HeifImageFile, check_heif_magic, register_heif_opener
from .constants import heif_filetype_maybe  # DEPRECATED
from .constants import heif_filetype_no  # DEPRECATED
from .constants import heif_filetype_yes_supported  # DEPRECATED
from .constants import heif_filetype_yes_unsupported  # DEPRECATED
from .constants import (
    HeifBrand,
    HeifChannel,
    HeifChroma,
    HeifColorProfileType,
    HeifColorspace,
    HeifCompressionFormat,
    HeifErrorCode,
    HeifFiletype,
)
from .error import HeifError
from .misc import reset_orientation

# pylint: disable=redefined-builtin
from .reader import (
    HeifFile,
    HeifThumbnail,
    UndecodedHeifFile,
    UndecodedHeifThumbnail,
    check,
    check_heif,
    get_file_mimetype,
    is_supported,
    open,
    open_heif,
    read,
    read_heif,
)
from .writer import write_heif
