"""
Options to change pillow_heif's runtime behaviour.
"""
from typing import Union


class PyLibHeifOptions:
    """Pillow-Heif runtime properties."""

    def __init__(self):
        self._cfg = {}
        self.reset()

    @property
    def thumbnails(self) -> bool:
        """Property to enable or disable HEIF thumbnails functionality.

        Default = ``True``"""

        return self._cfg["thumbnails"]

    @thumbnails.setter
    def thumbnails(self, value: bool):
        self._cfg["thumbnails"] = value

    @property
    def quality(self) -> Union[int, None]:
        """Get or set default encoding quality.

        .. note:: Quality specified during :py:meth:`~pillow_heif.HeifFile.save`
            has higher priority then this.

        Possible values: None, -1, range(0-100). Default=None
            Set -1 for lossless quality or from 0 to 100, where 0 is lowest and 100 is highest.

        .. note:: Also for lossless encoding you should specify ``chroma=444`` during save."""

        return self._cfg["quality"]

    @quality.setter
    def quality(self, value):
        self._cfg["quality"] = value

    @property
    def save_to_12bit(self) -> bool:
        """Should 16 bit images be saved to 12 bit instead of 10. Default = ``False``"""

        return self._cfg["save_to_12bit"]

    @save_to_12bit.setter
    def save_to_12bit(self, value):
        self._cfg["save_to_12bit"] = value

    def update(self, **kwargs) -> None:
        """Method to update multiple values in configuration at the same time."""

        _keys = kwargs.keys()
        for k in ("thumbnails", "quality", "save_to_12bit"):
            if k in _keys:
                setattr(self, k, kwargs[k])

    def reset(self) -> None:
        """Method for restoring default configuration values."""

        self._cfg["thumbnails"] = True
        self._cfg["quality"] = None
        self._cfg["save_to_12bit"] = False


CFG_OPTIONS: PyLibHeifOptions = PyLibHeifOptions()


def options() -> PyLibHeifOptions:
    """Wrapper function to return runtime options variable.

    :returns: A :py:class:`~pillow_heif._options.PyLibHeifOptions` class."""

    return CFG_OPTIONS
