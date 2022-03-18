"""
Options to change pillow_heif runtime behaviour.
"""

from ._lib_info import have_decoder_for_format, have_encoder_for_format
from .constants import HeifCompressionFormat


class PyLibHeifOptions:
    def __init__(self):
        self._hevc_enc = have_encoder_for_format(HeifCompressionFormat.HEVC)
        self._avif_dec = have_decoder_for_format(HeifCompressionFormat.AV1)
        self._cfg = {}
        self.reset()

    @property
    def hevc_enc(self):
        return self._hevc_enc

    @property
    def avif_dec(self):
        return self._avif_dec

    @property
    def avif(self) -> bool:
        return self._cfg["avif"]

    @avif.setter
    def avif(self, value: bool):
        self._cfg["avif"] = value if self._avif_dec else False

    @property
    def strict(self) -> bool:
        return self._cfg["strict"]

    @strict.setter
    def strict(self, value: bool):
        self._cfg["strict"] = value

    @property
    def thumbnails(self) -> bool:
        return self._cfg["thumbnails"]

    @thumbnails.setter
    def thumbnails(self, value: bool):
        self._cfg["thumbnails"] = value

    @property
    def thumbnails_autoload(self) -> bool:
        return self._cfg["thumbnails_autoload"]

    @thumbnails_autoload.setter
    def thumbnails_autoload(self, value: bool):
        self._cfg["thumbnails_autoload"] = value

    def update(self, **kwargs) -> None:
        _keys = kwargs.keys()
        for k in ("avif", "strict", "thumbnails", "thumbnails_autoload"):
            if k in _keys:
                setattr(self, k, kwargs[k])

    def reset(self) -> None:
        self._cfg["avif"] = self.avif_dec
        self._cfg["strict"] = False
        self._cfg["thumbnails"] = False
        self._cfg["thumbnails_autoload"] = False


CFG_OPTIONS: PyLibHeifOptions = PyLibHeifOptions()


def options() -> PyLibHeifOptions:
    return CFG_OPTIONS
