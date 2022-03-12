"""
Options to change pillow_heif runtime behaviour.
"""

from .constants import HeifCompressionFormat
from ._lib_info import have_decoder_for_format, have_encoder_for_format


class PyLibHeifOptions:
    def __init__(self):
        self._avif_enc = have_encoder_for_format(HeifCompressionFormat.AV1)
        self._avif_dec = have_decoder_for_format(HeifCompressionFormat.AV1)
        self._cfg = {}
        self.reset()

    @property
    def avif_enc(self):
        return self._avif_enc

    @property
    def avif_dec(self):
        return self._avif_dec

    @property
    def avif(self) -> bool:
        return self._cfg["avif"]

    @avif.setter
    def avif(self, value: bool):
        if value and not self._avif_dec:
            return
        self._cfg["avif"] = value

    @property
    def strict(self) -> bool:
        return self._cfg["strict"]

    @strict.setter
    def strict(self, value: bool):
        self._cfg["strict"] = value

    def update(self, **kwargs) -> None:
        _keys = kwargs.keys()
        if "avif" in _keys:
            self.avif = kwargs["avif"]
        if "strict" in _keys:
            self.strict = kwargs["strict"]

    def reset(self) -> None:
        self._cfg["avif"] = self.avif_dec
        self._cfg["strict"] = False


CFG_OPTIONS: PyLibHeifOptions = PyLibHeifOptions()


def options() -> PyLibHeifOptions:
    """Returns class for runtime behaviour configuration."""
    return CFG_OPTIONS
