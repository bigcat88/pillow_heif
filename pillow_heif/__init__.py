# pylint: disable=unused-import
# pylint: disable=redefined-builtin
from .constants import *  # pylint: disable=unused-wildcard-import
from .reader import (
    HeifFile,
    UndecodedHeifFile,
    check,
    read,
    open,
)
from .writer import write
from .error import HeifError
from .as_opener import register_heif_opener, check_heif_magic
from ._version import __version__
from ._lib_version import libheif_version
