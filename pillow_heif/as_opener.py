"""
Opener for Pillow library.
"""

from warnings import warn

from PIL import Image, ImageFile

from ._options import options
from .error import HeifError
from .misc import reset_orientation
from .reader import UndecodedHeifFile, is_supported, open_heif


class HeifImageFile(ImageFile.ImageFile):
    format = "HEIF"
    format_description = "HEIF image"
    heif_file = None

    def _open(self):
        try:
            heif_file = open_heif(self.fp)
        except HeifError as exception:
            raise SyntaxError(str(exception)) from None
        self.heif_file = heif_file
        self._init_from_undecoded_heif(heif_file)
        self.info["original_orientation"] = reset_orientation(self.info)
        self.tile = []
        if getattr(self, "_exclusive_fp", False) and getattr(self, "fp", None):
            self.fp.close()
        self.fp = None

    def verify(self) -> None:
        pass  # we already check this in `_open`, no need to check second time.

    def load(self):
        if self.heif_file:
            heif_file = self.heif_file.load()
            self.load_prepare()
            self.frombytes(heif_file.data, "raw", (self.mode, heif_file.stride))
            self.heif_file.data = None
            self.heif_file = None
        return super().load()

    def _init_from_undecoded_heif(self, heif_file: UndecodedHeifFile) -> None:
        self._size = heif_file.size
        self.mode = heif_file.mode
        for k in ("brand", "exif", "metadata", "color_profile"):
            self.info[k] = heif_file.info[k]
        for k in ("icc_profile", "nclx_profile"):
            if k in heif_file.info:
                self.info[k] = heif_file.info[k]
        self.info["thumbnails"] = heif_file.thumbnails
        self.info["top_lvl_images"] = heif_file.top_lvl_images


def register_heif_opener(**kwargs):
    options().update(**kwargs)
    Image.register_open(HeifImageFile.format, HeifImageFile, is_supported)
    extensions = [".heic", ".hif"]
    Image.register_mime(HeifImageFile.format, "image/heic")
    Image.register_mime(HeifImageFile.format, "image/heif")
    if options().avif:
        extensions.append(".avif")
        Image.register_mime(HeifImageFile.format, "image/avif")
    Image.register_extensions(HeifImageFile.format, extensions)


# --------------------------------------------------------------------
# DEPRECATED FUNCTIONS.


def check_heif_magic(data) -> bool:
    warn("Function `check_heif_magic` is deprecated, use `is_supported` instead.", DeprecationWarning)
    return is_supported(data)  # pragma: no cover
