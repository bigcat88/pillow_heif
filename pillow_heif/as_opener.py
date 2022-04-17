"""
Opener for Pillow library.
"""

from copy import deepcopy
from typing import Any

from PIL import Image, ImageFile

from ._options import options
from .error import HeifError
from .heif import HeifImage, from_pillow, is_supported, open_heif
from .misc import reset_orientation


class HeifImageFile(ImageFile.ImageFile):
    format = "HEIF"
    format_description = "HEIF container for HEVC and AV1"
    heif_file: Any
    _close_exclusive_fp_after_loading = False

    def __init__(self, *args, **kwargs):
        self.heif_file = None
        super().__init__(*args, **kwargs)

    def _open(self):
        try:
            heif_file = open_heif(self.fp)
        except HeifError as exception:
            raise SyntaxError(str(exception)) from None
        self.heif_file = heif_file
        self._init_from_heif_file(heif_file)
        self.tile = []

    def load(self):
        if self.heif_file:
            frame_heif = self._heif_file_by_index(self.tell())
            self.load_prepare()
            self.frombytes(frame_heif.data, "raw", (self.mode, frame_heif.stride))
            if self.is_animated:
                frame_heif.unload()
            else:
                self.info["thumbnails"] = deepcopy(self.info["thumbnails"])
                self.heif_file = None
                self._close_exclusive_fp_after_loading = True
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
        for _ in self.heif_file.thumbnails_all():
            _.load()

    @property
    def n_frames(self):
        return len(self.heif_file) if self.heif_file else 1

    @property
    def is_animated(self):
        return self.n_frames > 1

    def _seek_check(self, frame):
        if frame < 0 or frame >= self.n_frames:
            raise EOFError("attempt to seek outside sequence")
        return self.tell() != frame

    def _heif_file_by_index(self, index) -> HeifImage:
        return self.heif_file[index]

    def _init_from_heif_file(self, heif_image) -> None:
        self._size = heif_image.size
        self.mode = heif_image.mode
        for k in ("main", "brand", "exif", "metadata", "img_id"):
            self.info[k] = heif_image.info[k]
        for k in ("icc_profile", "icc_profile_type", "nclx_profile"):
            if k in heif_image.info:
                self.info[k] = heif_image.info[k]
        self.info["thumbnails"] = heif_image.thumbnails
        self.info["original_orientation"] = reset_orientation(self.info)


def _save(im, fp, _filename):
    from_pillow(im, load_one=True).save(fp, save_all=False, **im.encoderinfo)


def _save_all(im, fp, _filename):
    from_pillow(im).save(fp, save_all=True, **im.encoderinfo)


def register_heif_opener(**kwargs):
    options().update(**kwargs)
    Image.register_open(HeifImageFile.format, HeifImageFile, is_supported)
    Image.register_save(HeifImageFile.format, _save)
    Image.register_save_all(HeifImageFile.format, _save_all)
    extensions = [".heic", ".heif", ".hif"]
    Image.register_mime(HeifImageFile.format, "image/heic")
    Image.register_mime(HeifImageFile.format, "image/heif")
    Image.register_mime(HeifImageFile.format, "image/heif-sequence")
    Image.register_extensions(HeifImageFile.format, extensions)
