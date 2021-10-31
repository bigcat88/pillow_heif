from .constants import *  # pylint: disable=unused-wildcard-import
from .reader import HeifFile, UndecodedHeifFile, check, read, open  # pylint: disable=redefined-builtin,unused-import
from .writer import write  # pylint: disable=unused-import
from .error import HeifError  # pylint: disable=unused-import
from .as_opener import register_heif_opener, check_heif_magic  # pylint: disable=unused-import
from . import _libheif   # pylint: disable=import-self


__version__ = "0.1.4"


def libheif_version():
    return _libheif.ffi.string(_libheif.lib.heif_get_version()).decode()
