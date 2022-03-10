"""
Options to change pillow_heif runtime behaviour.
"""


from .constants import HeifCompressionFormat
from ._lib_info import have_decoder_for_format


def _get_default_cfg_options() -> dict:
    return {
        "avif": have_decoder_for_format(HeifCompressionFormat.AV1),
        "strict": False,
    }


OPTIONS = _get_default_cfg_options()


def get_cfg_options() -> dict:
    return OPTIONS


def reset_cfg_options() -> None:
    get_cfg_options().clear()
    get_cfg_options().update(_get_default_cfg_options())
