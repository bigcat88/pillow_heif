"""
Functions to get version and encoders/decoders info of embedded C libraries.
"""


from _pillow_heif_cffi import ffi, lib

from .constants import HeifCompressionFormat


def libheif_version() -> str:
    """Wrapper around `libheif.heif_get_version`"""
    return ffi.string(lib.heif_get_version()).decode()


def have_decoder_for_format(format_id: HeifCompressionFormat) -> bool:
    """Wrapper around `libheif.heif_have_decoder_for_format`"""
    return lib.heif_have_decoder_for_format(format_id)


def have_encoder_for_format(format_id: HeifCompressionFormat) -> bool:
    """Wrapper around `libheif.heif_have_encoder_for_format`"""
    return lib.heif_have_encoder_for_format(format_id)


def libheif_info() -> dict:
    """Returns dictionary with avalaible decoders & encoders and libheif version.
    Avalaible keys are `version`, `decoders`, `encoders` and `en_de_coders`.
    `en_de_coders.values` = `encoders.values()` & `decoders.values()`
    """
    decoders = {}
    encoders = {}
    for format_id in (HeifCompressionFormat.HEVC, HeifCompressionFormat.AV1, HeifCompressionFormat.AVC):
        decoders[format_id.name] = have_decoder_for_format(format_id)
        encoders[format_id.name] = have_encoder_for_format(format_id)
    en_de_coders = {k: v and encoders[k] for k, v in decoders.items()}
    return {"version": libheif_version(), "decoders": decoders, "encoders": encoders, "en_de_coders": en_de_coders}
