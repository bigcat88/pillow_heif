"""
Opener for Pillow library.
"""

from warnings import warn
from PIL import Image, ImageFile

from .reader import is_supported, open_heif, UndecodedHeifFile
from .error import HeifError
from ._options import options


class HeifImageFile(ImageFile.ImageFile):
    format = "HEIF"
    format_description = "HEIF image"
    heif_file = None

    def _open(self):
        try:
            heif_file = open_heif(self.fp)
        except HeifError as e:
            raise SyntaxError(str(e)) from None
        if hasattr(self, "_exclusive_fp") and self._exclusive_fp and self.fp:
            self.fp.close()
        self.fp = None
        self.heif_file = heif_file
        self._init_from_undecoded_heif(heif_file)
        self.tile = []

    def _init_from_undecoded_heif(self, heif_file: UndecodedHeifFile) -> None:
        self._size = heif_file.size
        self.mode = heif_file.mode
        for k in ("brand", "exif", "metadata", "color_profile"):
            self.info[k] = heif_file.info[k]
        for k in ("icc_profile", "nclx_profile"):
            if k in heif_file.info:
                self.info[k] = heif_file.info[k]

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


def register_heif_opener(**kwargs):
    options().update(**kwargs)
    Image.register_open(HeifImageFile.format, HeifImageFile, is_supported)
    extensions = [".heic", ".hif"]
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
