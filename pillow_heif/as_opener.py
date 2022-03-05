"""
Opener for Pillow library.
"""

from PIL import Image, ImageFile

from .constants import heif_filetype_no
from .reader import open_heif, check_heif
from .error import HeifError


class HeifImageFile(ImageFile.ImageFile):
    format = "HEIF"
    format_description = "HEIF/HEIC image"
    color_profile = None
    heif_file = None

    def _open(self):
        try:
            heif_file = open_heif(self.fp)
        except HeifError as e:
            raise SyntaxError(str(e)) from None
        if hasattr(self, "_exclusive_fp") and self._exclusive_fp:
            if hasattr(self, "fp") and self.fp:
                self.fp.close()
        self.fp = None
        self._size = heif_file.size
        self.mode = heif_file.mode

        if heif_file.metadata:
            for data in heif_file.metadata:
                if data["type"] == "Exif":
                    self.info["exif"] = data["data"]
                    break

        if heif_file.color_profile:
            self.color_profile = heif_file.color_profile
            if heif_file.color_profile["type"] in ("rICC", "prof"):
                self.info["icc_profile"] = heif_file.color_profile["data"]
        self.tile = []
        self.heif_file = heif_file

    def verify(self) -> None:
        pass  # we already check this in `_open`, no need to check second time.

    def load(self):
        if self.heif_file is not None and self.heif_file:
            heif_file = self.heif_file.load()
            self.load_prepare()
            self.frombytes(heif_file.data, "raw", (self.mode, heif_file.stride))
            self.heif_file.data = None
            self.heif_file = None
        return super().load()


def check_heif_magic(data) -> bool:
    return check_heif(data) != heif_filetype_no


def register_heif_opener():
    Image.register_open(HeifImageFile.format, HeifImageFile, check_heif_magic)
    Image.register_mime(HeifImageFile.format, "image/heif")
    Image.register_mime(HeifImageFile.format, "image/avif")
    Image.register_extensions(HeifImageFile.format, [".heic", ".heif", ".avif"])
