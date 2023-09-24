"""Functions to get versions of underlying libraries."""

try:
    import _pillow_heif
except ImportError as ex:
    from ._deffered_error import DeferredError

    _pillow_heif = DeferredError(ex)


def libheif_version() -> str:
    """Returns ``libheif`` version."""
    return _pillow_heif.lib_info["libheif"]


def libheif_info() -> dict:
    """Returns a dictionary with version information.

    The keys `libheif`, `HEIF`, `AVIF` are always present, but values for `HEIF`/`AVIF` can be empty.

    {
        'libheif': '1.14.2',
        'HEIF': 'x265 HEVC encoder (3.4+31-6722fce1f)',
        'AVIF': 'AOMedia Project AV1 Encoder 3.5.0'
    }
    """
    return _pillow_heif.lib_info
