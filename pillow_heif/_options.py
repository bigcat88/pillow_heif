"""
Options to change pillow_heif's runtime behaviour.
"""
from typing import Union
from warnings import warn


class PyLibHeifOptions:
    """Pillow-Heif runtime properties."""

    def __init__(self):
        self._cfg = {}
        self.reset()

    @property
    def strict(self) -> bool:
        """Indicates should be or not partially supported files be marked as supported.
        Affects on return result of :py:func:`~pillow_heif.is_supported` function
        and on algorithm of accepting images of ``HeifImagePlugin``.

        Default = ``False``

        ``DEPRECATED``, will be removed in ``0.8.0``"""

        return self._cfg["strict"]  # pragma: no cover

    @strict.setter
    def strict(self, value: bool):
        warn(
            "`strict` option is marked as deprecated and will be removed in a future.",
            DeprecationWarning,
        )
        self._cfg["strict"] = value  # pragma: no cover

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
    def ctx_in_memory(self) -> bool:
        """Should files be read to memory fully.

        As Python is much slower than ``C++``, we read a file to memory and let ``libheif`` manage reads.
        You can look at source of class ``LibHeifCtx`` in ``_libheif_ctx.py`` file.
        Deprecated, will be removed in ``0.8.0`` version.

        Default = ``True``

        ``DEPRECATED``, will be removed in ``0.8.0``"""

        return self._cfg["ctx_in_memory"]

    @ctx_in_memory.setter
    def ctx_in_memory(self, value):
        warn(
            "`ctx_in_memory` is marked as deprecated and will be removed in a future."
            " There is no particular reason to read the file partially, as tests show",
            DeprecationWarning,
        )
        self._cfg["ctx_in_memory"] = value

    @property
    def save_to_12bit(self) -> bool:
        """Should 16 bit images be saved to 12 bit instead of 10. Default = ``False``"""

        return self._cfg["save_to_12bit"]

    @save_to_12bit.setter
    def save_to_12bit(self, value):
        self._cfg["save_to_12bit"] = value

    def update(self, **kwargs) -> None:
        """Method for at once update multiply values in config."""

        _keys = kwargs.keys()
        for k in ("strict", "thumbnails", "quality", "ctx_in_memory", "save_to_12bit"):
            if k in _keys:
                setattr(self, k, kwargs[k])

    def reset(self) -> None:
        """Use this for reset config values to their defaults."""

        self._cfg["strict"] = False
        self._cfg["thumbnails"] = True
        self._cfg["quality"] = None
        self._cfg["ctx_in_memory"] = True
        self._cfg["save_to_12bit"] = False


CFG_OPTIONS: PyLibHeifOptions = PyLibHeifOptions()


def options() -> PyLibHeifOptions:
    """Wrapper function to return runtime options variable.

    :returns: A :py:class:`~pillow_heif._options.PyLibHeifOptions` class."""

    return CFG_OPTIONS
