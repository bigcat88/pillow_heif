# pylint: disable=unused-import
from .constants import *  # pylint: disable=unused-wildcard-import
from .reader import HeifFile, UndecodedHeifFile, check, read, open  # pylint: disable=redefined-builtin
from .writer import write
from .error import HeifError
from .as_opener import register_heif_opener, check_heif_magic
from . import _libheif   # pylint: disable=import-self
from . import _version


__version__ = _version.__version__


def libheif_version():
    return _libheif.ffi.string(_libheif.lib.heif_get_version()).decode()
