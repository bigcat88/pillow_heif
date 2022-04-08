import builtins
import os
import sys
from pathlib import Path
from platform import machine
from warnings import warn

import pytest

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))

avif_images = [f for f in list(Path().glob("images/avif/*.avif"))] + [f for f in list(Path().glob("images/*.avif"))]
heic_images = [f for f in list(Path().glob("images/nokia/*.heic"))] + [f for f in list(Path().glob("images/*.heic"))]
heif_images = [f for f in list(Path().glob("images/*.hif"))] + [f for f in list(Path().glob("images/*.heif"))]

if not pillow_heif.options().avif:
    warn("Skipping tests for `AV1` format due to lack of codecs.")
    avif_images.clear()

images_dataset = heic_images + avif_images + heif_images


def test_libheif_info():
    info = pillow_heif.libheif_info()
    assert info["decoders"]["HEVC"]
    if machine().find("armv7") != -1:
        return
    assert info["decoders"]["AV1"]
    if sys.maxsize > 2**32:
        assert info["encoders"]["HEVC"]
        assert pillow_heif.options().hevc_enc


def test_lib_version():
    assert pillow_heif.libheif_version() == "1.12.0"


def test_debug_boxes_dump():
    heif_file = pillow_heif.open_heif(list(Path().glob("images/*.heic"))[0])
    heif_file._debug_dump("debug_dump.txt")
    assert Path("debug_dump.txt").stat().st_size > 100
    Path("debug_dump.txt").unlink()


@pytest.mark.parametrize("img_path", images_dataset)
def test_get_file_mimetype(img_path):
    mimetype = pillow_heif.get_file_mimetype(img_path)
    assert mimetype in ("image/heic", "image/heif", "image/heif-sequence", "image/avif")


@pytest.mark.parametrize("img_path", images_dataset)
def test_heif_check_filetype(img_path):
    with builtins.open(img_path, "rb") as fh:
        assert pillow_heif.check_heif(fh) != pillow_heif.HeifFiletype.NO
        assert pillow_heif.is_supported(fh)


def test_heif_str():
    heif_file = pillow_heif.open_heif(Path("images/pug_1_1.heic"))
    assert str(heif_file).find("HeifFile with 1 image") != -1
    assert str(heif_file).find("no image data") != -1
    assert str(heif_file[0]).find("HeifImage 445x496 RGB") != -1
    assert str(heif_file[0]).find("no image data") != -1
    assert str(heif_file.thumbnails[0]).find("HeifThumbnail 228x256 RGB") != -1
    assert str(heif_file.thumbnails[0]).find("no image data") != -1
