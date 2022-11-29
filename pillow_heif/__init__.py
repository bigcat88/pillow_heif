"""
Import all possible stuff that can be used.
"""


from . import options
from ._lib_info import libheif_info, libheif_version
from ._version import __version__
from .as_plugin import (
    AvifImageFile,
    HeifImageFile,
    register_avif_opener,
    register_heif_opener,
)
from .constants import HeifErrorCode
from .error import HeifError
from .heif import (
    HeifFile,
    HeifImage,
    HeifThumbnail,
    from_bytes,
    from_pillow,
    is_supported,
    open_heif,
    read_heif,
)
from .misc import get_file_mimetype, set_orientation
from .thumbnails import add_thumbnails, thumbnail
