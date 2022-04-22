import builtins
import os
import sys
from pathlib import Path
from platform import machine

import dataset
import pytest

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))


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


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_get_file_mimetype(img_path):
    mimetype = pillow_heif.get_file_mimetype(img_path)
    assert mimetype in ("image/heic", "image/heif", "image/heif-sequence", "image/avif")


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_heif_check_filetype(img_path):
    with builtins.open(img_path, "rb") as fh:
        assert pillow_heif.check_heif(fh) != pillow_heif.HeifFiletype.NO
        assert pillow_heif.is_supported(fh)


def test_heif_str():
    heif_file = pillow_heif.open_heif(Path("images/rgb8_128_128_2_1.heic"))
    assert str(heif_file).find("HeifFile with 2 images") != -1
    assert str(heif_file).find("no image data") != -1
    assert str(heif_file[0]).find("HeifImage 128x128 RGB") != -1
    assert str(heif_file[0]).find("no image data") != -1
    assert str(heif_file.thumbnails[0]).find("HeifThumbnail 64x64 RGB") != -1
    assert str(heif_file.thumbnails[0]).find("no image data") != -1
