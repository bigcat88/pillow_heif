"""
Opener for Pillow library.
"""

from typing import Union
from warnings import warn

from PIL import Image, ImageFile

from ._options import options
from .error import HeifError
from .misc import reset_orientation
from .reader import HeifFile, UndecodedHeifFile, is_supported, open_heif


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
        self._init_from_heif_file(heif_file)
        self.tile = []
        # We don't need any data from `fp` to work. Maybe only in near future for save operations.
        if getattr(self, "_exclusive_fp", False) and getattr(self, "fp", None):
            self.fp.close()
        self.fp = None

    def load(self):
        if self.heif_file:
            frame_heif = self._heif_file_by_index(self.tell())
            frame_heif.load()
            self.load_prepare()
            self.frombytes(frame_heif.data, "raw", (self.mode, frame_heif.stride))
            if not self.is_animated:
                self.heif_file.data = None
                self.heif_file = None
        return super().load()

    def seek(self, frame):
        if not self._seek_check(frame):
            return
        self._init_from_heif_file(self._heif_file_by_index(frame))

    def tell(self):
        i = 0
        if self.heif_file:
            for heif in self.heif_file:
                if self.info["img_id"] == heif.info["img_id"]:
                    break
                i += 1
        return i

    def verify(self) -> None:
        pass  # we already check this in `_open`, no need to check second time.

    @property
    def n_frames(self):
        return 1 + len(self.info["top_lvl_images"])

    @property
    def is_animated(self):
        return self.n_frames > 1

    def _seek_check(self, frame):
        if frame < 0 or frame > len(self.info["top_lvl_images"]):
            raise EOFError("attempt to seek outside sequence")
        return self.tell() != frame

    def _heif_file_by_index(self, index):
        return self.heif_file[index]

    def _init_from_heif_file(self, heif_file: Union[UndecodedHeifFile, HeifFile]) -> None:
        self._size = heif_file.size
        self.mode = heif_file.mode
        for k in ("brand", "exif", "metadata", "color_profile", "img_id"):
            self.info[k] = heif_file.info[k]
        for k in ("icc_profile", "nclx_profile"):
            if k in heif_file.info:
                self.info[k] = heif_file.info[k]
        self.info["thumbnails"] = heif_file.thumbnails
        if heif_file.info["main"]:
            self.info["top_lvl_images"] = heif_file.top_lvl_images
        self.info["original_orientation"] = reset_orientation(self.info)


def register_heif_opener(**kwargs):
    options().update(**kwargs)
    Image.register_open(HeifImageFile.format, HeifImageFile, is_supported)
    extensions = [".heic", ".heif", ".hif"]
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
