"""
Plugins for Pillow library.
"""

from typing import Any
from warnings import warn

from PIL import Image, ImageFile

from ._lib_info import have_decoder_for_format, have_encoder_for_format
from ._options import options
from .constants import HeifCompressionFormat, HeifErrorCode
from .error import HeifError
from .heif import HeifFile, open_heif
from .misc import _get_bytes, getxmp, set_orientation


class _LibHeifImageFile(ImageFile.ImageFile):
    """Base class with all functionality for ``HeifImageFile`` and ``AvifImageFile`` classes."""

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
        self.__frame = heif_file.primary_index()
        self._init_from_heif_file(self.__frame)
        self.tile = []

    def load(self):
        if self.heif_file:
            frame_heif = self.heif_file[self.tell()]
            self.load_prepare()
            try:
                self.frombytes(frame_heif.data, "raw", (frame_heif.mode, frame_heif.stride))
            except HeifError as exc:
                truncated = exc.code == HeifErrorCode.DECODER_PLUGIN_ERROR and exc.subcode == 100
                if not truncated or not ImageFile.LOAD_TRUNCATED_IMAGES:
                    raise
            if not self.is_animated:
                self.info["thumbnails"] = [i.clone_nd() for i in self.info["thumbnails"]]
                self.heif_file = None
                self._close_exclusive_fp_after_loading = True
                if self.fp and getattr(self, "_exclusive_fp", False) and hasattr(self.fp, "close"):
                    self.fp.close()
                self.fp = None
        return super().load()

    def getxmp(self) -> dict:
        """Returns a dictionary containing the XMP tags. Requires ``defusedxml`` to be installed.

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
        pass

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


class HeifImageFile(_LibHeifImageFile):
    """Pillow plugin class type for a HEIF image format."""

    format = "HEIF"
    format_description = "HEIF container"


def _is_supported_heif(fp) -> bool:
    magic = _get_bytes(fp, 12)
    if magic[4:8] != b"ftyp":
        return False
    if magic[8:12] in (
        b"heic",
        b"heix",
        b"heim",
        b"heis",
        b"hevc",
        b"hevx",
        b"hevm",
        b"hevs",
        b"mif1",
        b"msf1",
    ):
        return True
    return False


def _save_heif(im, fp, _filename):
    heif_file = HeifFile().add_from_pillow(im, load_one=True, for_encoding=True)
    heif_file.save(fp, save_all=False, **im.encoderinfo, dont_copy=True)


def _save_all_heif(im, fp, _filename):
    heif_file = HeifFile().add_from_pillow(im, ignore_primary=False, for_encoding=True)
    heif_file.save(fp, save_all=True, **im.encoderinfo, dont_copy=True)


def register_heif_opener(**kwargs) -> None:
    """Registers a Pillow plugin for HEIF format.

    :param kwargs: dictionary with values to set in :py:class:`~pillow_heif._options.PyLibHeifOptions`
    """

    options().update(**kwargs)
    Image.register_open(HeifImageFile.format, HeifImageFile, _is_supported_heif)
    if have_encoder_for_format(HeifCompressionFormat.HEVC):
        Image.register_save(HeifImageFile.format, _save_heif)
        Image.register_save_all(HeifImageFile.format, _save_all_heif)
    extensions = [".heic", ".heics", ".heif", ".heifs", ".hif"]
    Image.register_mime(HeifImageFile.format, "image/heif")
    Image.register_extensions(HeifImageFile.format, extensions)


class AvifImageFile(_LibHeifImageFile):
    """Pillow plugin class type for an AVIF image format."""

    format = "AVIF"
    format_description = "AVIF container"


def _is_supported_avif(fp) -> bool:
    magic = _get_bytes(fp, 12)
    if magic[4:8] != b"ftyp":
        return False
    if magic[8:12] in (
        b"avif",
        # b"avis",
    ):
        return True
    return False


def _save_avif(im, fp, _filename):
    heif_file = HeifFile().add_from_pillow(im, load_one=True, for_encoding=True)
    heif_file.save(fp, save_all=False, **im.encoderinfo, dont_copy=True, format="AVIF")


def _save_all_avif(im, fp, _filename):
    heif_file = HeifFile().add_from_pillow(im, ignore_primary=False, for_encoding=True)
    heif_file.save(fp, save_all=True, **im.encoderinfo, dont_copy=True, format="AVIF")


def register_avif_opener(**kwargs) -> None:
    """Registers a Pillow plugin for AVIF format.

    :param kwargs: dictionary with values to set in :py:class:`~pillow_heif._options.PyLibHeifOptions`
    """

    if not have_decoder_for_format(HeifCompressionFormat.AV1) and not have_encoder_for_format(
        HeifCompressionFormat.AV1
    ):
        warn("This version of `pillow-heif` was built without AVIF support.")
        return
    options().update(**kwargs)
    if have_decoder_for_format(HeifCompressionFormat.AV1):
        Image.register_open(AvifImageFile.format, AvifImageFile, _is_supported_avif)
    if have_encoder_for_format(HeifCompressionFormat.AV1):
        Image.register_save(AvifImageFile.format, _save_avif)
        Image.register_save_all(AvifImageFile.format, _save_all_avif)
    # extensions = [".avif", ".avifs"]
    extensions = [".avif"]
    Image.register_mime(AvifImageFile.format, "image/avif")
    Image.register_extensions(AvifImageFile.format, extensions)
