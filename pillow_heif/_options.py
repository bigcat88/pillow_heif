"""
Options to change pillow_heif's runtime behaviour.
"""
from typing import Union

from ._lib_info import have_decoder_for_format, have_encoder_for_format
from .constants import HeifCompressionFormat


class PyLibHeifOptions:
    """Pillow-Heif runtime properties."""

    def __init__(self):
        self._hevc_enc = have_encoder_for_format(HeifCompressionFormat.HEVC)
        self._avif_dec = have_decoder_for_format(HeifCompressionFormat.AV1)
        self._cfg = {}
        self.reset()

    @property
    def hevc_enc(self) -> bool:
        """Read only property showing if library was build with h265 HEVC encoder."""
        return self._hevc_enc

    @property
    def avif(self) -> bool:
        """Enable or disable x264(AVIF) file read support. Default=True(if build include libaom)"""
        return self._cfg["avif"]

    @avif.setter
    def avif(self, value: bool):
        self._cfg["avif"] = value if self._avif_dec else False

    @property
    def strict(self) -> bool:
        """
        Indicates should be or not partially supported files be marked as supported.
        Affects on return result of :py:func:`~pillow_heif.is_supported` function.
        """
        return self._cfg["strict"]

    @strict.setter
    def strict(self, value: bool):
        self._cfg["strict"] = value

    @property
    def thumbnails(self) -> bool:
        """Property to enable or disable HEIF thumbnails functionality. Default=True"""
        return self._cfg["thumbnails"]

    @thumbnails.setter
    def thumbnails(self, value: bool):
        self._cfg["thumbnails"] = value

    @property
    def quality(self) -> Union[int, None]:
        """
        Get or set encoding quality.

        Possible values: None, -1, range(0-100). Default=None
            Set -1 for lossless quality or from 0 to 100, where 0 is lowest and 100 is highest.
        """
        return self._cfg["quality"]

    @quality.setter
    def quality(self, value):
        self._cfg["quality"] = value

    def update(self, **kwargs) -> None:
        """Method for at once update multiply values in config."""
        _keys = kwargs.keys()
        for k in ("avif", "strict", "thumbnails", "quality"):
            if k in _keys:
                setattr(self, k, kwargs[k])

    def reset(self) -> None:
        """Use this for reset config values to their defaults."""
        self._cfg["avif"] = self._avif_dec
        self._cfg["strict"] = False
        self._cfg["thumbnails"] = True
        self._cfg["quality"] = None


CFG_OPTIONS: PyLibHeifOptions = PyLibHeifOptions()


def options() -> PyLibHeifOptions:
    """
    Wrapper function to return runtime options variable.

    :returns: A :py:class:`~pillow_heif._options.PyLibHeifOptions` class.
    """

    return CFG_OPTIONS
