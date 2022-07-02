"""
Plugin for Pillow library.
"""

from copy import deepcopy
from typing import Any

from PIL import Image, ImageFile

from ._options import options
from .constants import HeifErrorCode
from .error import HeifError
from .heif import HeifFile, is_supported, open_heif
from .misc import getxmp, set_orientation


class HeifImageFile(ImageFile.ImageFile):
    """Pillow plugin class for HEIF image format."""

    format = "HEIF"
    format_description = "HEIF container for HEVC and AV1"
    heif_file: Any
    _close_exclusive_fp_after_loading = False

    def __init__(self, *args, **kwargs):
        self.__frame = 0
        self.heif_file = None
        super().__init__(*args, **kwargs)

    def _open(self):
        try:
            heif_file = open_heif(self.fp)
        except HeifError as exception:
            raise SyntaxError(str(exception)) from None
        self.custom_mimetype = heif_file.mimetype
        self.heif_file = heif_file
        self._init_from_heif_file(self.__frame)
        self.tile = []

    def load(self):
        if self.heif_file:
            frame_heif = self.heif_file[self.tell()]
            self.load_prepare()
            truncated = False
            try:
                self.frombytes(frame_heif.data, "raw", (frame_heif.mode, frame_heif.stride))
            except HeifError as exc:
                truncated = exc.code == HeifErrorCode.DECODER_PLUGIN_ERROR and exc.subcode == 100
                if not truncated or not ImageFile.LOAD_TRUNCATED_IMAGES:
                    raise
            if self.is_animated:
                frame_heif.unload()
            else:
                self.info["thumbnails"] = deepcopy(self.info["thumbnails"]) if not truncated else []
                self.heif_file = None
                self._close_exclusive_fp_after_loading = True
                if self.fp and getattr(self, "_exclusive_fp", False) and hasattr(self.fp, "close"):
                    self.fp.close()
                self.fp = None
        return super().load()

    def getxmp(self) -> dict:
        """Returns a dictionary containing the XMP tags.
        Requires defusedxml to be installed.

        :returns: XMP tags in a dictionary."""

        return getxmp(self.info["xmp"])

    def seek(self, frame):
        if not self._seek_check(frame):
            return
        self.__frame = frame
        self._init_from_heif_file(frame)
        _exif = getattr(self, "_exif", None)  # Pillow 9.2+ do no reload exif between frames.
        if _exif is not None:
            if getattr(_exif, "_loaded", None):
                _exif._loaded = False  # pylint: disable=protected-access

    def tell(self):
        return self.__frame

    def verify(self) -> None:
        for _ in self.info["thumbnails"]:
            _.load()

    @property
    def n_frames(self) -> int:
        """Return the number of available frames.

        :returns: Frame number, starting with 0."""

        return len(self.heif_file) if self.heif_file else 1

    @property
    def is_animated(self) -> bool:
        """Return ``True`` if this image has more then one frame, or ``False`` otherwise."""

        return self.n_frames > 1

    def _seek_check(self, frame):
        if frame < 0 or frame >= self.n_frames:
            raise EOFError("attempt to seek outside sequence")
        return self.tell() != frame

    def _init_from_heif_file(self, img_index: int) -> None:
        self._size = self.heif_file[img_index].size
        self.mode = self.heif_file[img_index].mode
        self.info = self.heif_file[img_index].info
        self.info["thumbnails"] = self.heif_file[img_index].thumbnails
        self.info["original_orientation"] = set_orientation(self.info)


def _save(im, fp, _filename):
    heif_file = HeifFile().add_from_pillow(im, load_one=True, for_encoding=True)
    heif_file.save(fp, save_all=False, **im.encoderinfo)


def _save_all(im, fp, _filename):
    heif_file = HeifFile().add_from_pillow(im, ignore_primary=False, for_encoding=True)
    heif_file.save(fp, save_all=True, **im.encoderinfo)


def register_heif_opener(**kwargs) -> None:
    """Registers Pillow plugin.

    :param kwargs: dictionary with values to set in :py:class:`~pillow_heif._options.PyLibHeifOptions`
    """

    options().update(**kwargs)
    Image.register_open(HeifImageFile.format, HeifImageFile, is_supported)
    Image.register_save(HeifImageFile.format, _save)
    Image.register_save_all(HeifImageFile.format, _save_all)
    extensions = [".heic", ".heif", ".hif"]
    Image.register_mime(HeifImageFile.format, "image/heic")
    Image.register_mime(HeifImageFile.format, "image/heif")
    Image.register_mime(HeifImageFile.format, "image/heif-sequence")
    Image.register_extensions(HeifImageFile.format, extensions)
