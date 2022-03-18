from platform import machine

from pillow_heif import libheif_info, libheif_version, options


def test_libheif_info():
    info = libheif_info()
    assert info["decoders"]["HEVC"]
    if machine().find("armv7") != -1:
        return
    assert info["decoders"]["AV1"]
    assert options().avif_dec
    assert info["encoders"]["HEVC"]
    assert options().hevc_enc


def test_lib_version():
    assert libheif_version() == "1.12.0"
