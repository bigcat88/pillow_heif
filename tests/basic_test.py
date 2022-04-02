import builtins
import os
from pathlib import Path
from platform import machine

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def test_libheif_info():
    info = pillow_heif.libheif_info()
    assert info["decoders"]["HEVC"]
    if machine().find("armv7") != -1:
        return
    assert info["decoders"]["AV1"]
    assert info["encoders"]["HEVC"]
    assert pillow_heif.options().hevc_enc


def test_lib_version():
    assert pillow_heif.libheif_version() == "1.12.0"


def test_debug_boxes_dump():
    heif_file = pillow_heif.open_heif(list(Path().glob("images/*.heic"))[0])
    heif_file.debug_dump("tmp/debug_dump.txt")
    assert Path("tmp/debug_dump.txt").stat().st_size > 100


def test_get_file_mimetype():
    for file in [*list(Path().glob("images/[!.]*.[!jt]*")), *list(Path().glob("images/avif/*.avif"))]:
        mimetype = pillow_heif.get_file_mimetype(file)
        assert mimetype in ("image/heic", "image/avif")


def test_heif_check_filetype():
    for file in [*list(Path().glob("images/[!.]*.[!jt]*")), *list(Path().glob("images/avif/*.avif"))]:
        with builtins.open(file, "rb") as fh:
            assert pillow_heif.check_heif(fh) != pillow_heif.HeifFiletype.NO
            assert pillow_heif.is_supported(fh)
