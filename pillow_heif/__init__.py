"""
Import all possible stuff that can be used.
"""

from ._lib_info import have_decoder_for_format, have_encoder_for_format, libheif_info, libheif_version
from ._options import options
from ._version import __version__
from .as_opener import HeifImageFile, check_heif_magic, register_heif_opener

# pylint: disable=unused-import
# pylint: disable=redefined-builtin
from .constants import *  # pylint: disable=unused-wildcard-import
from .error import HeifError
from .reader import (
    HeifFile,
    HeifThumbnail,
    UndecodedHeifFile,
    UndecodedHeifThumbnail,
    check,
    check_heif,
    is_supported,
    open,
    open_heif,
    read,
    read_heif,
)
from .writer import write_heif
