from .constants import *
from .reader import *
from .writer import *
from .error import HeifError
from .as_opener import register_heif_opener, check_heif_magic
from . import _libheif


__version__ = "0.1.3"


def libheif_version():
    return _libheif.ffi.string(_libheif.lib.heif_get_version()).decode()
