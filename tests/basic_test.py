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
    assert mimetype in ("image/heic", "image/heif", "image/avif", "image/heic-sequence", "image/heif-sequence")


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_heif_check_filetype(img_path):
    with builtins.open(img_path, "rb") as fh:
        assert pillow_heif.check_heif(fh) != pillow_heif.HeifFiletype.NO
        assert pillow_heif.is_supported(fh)


def test_heif_str():
    str_heif_img_not_loaded = "<HeifImage 128x128 RGBA with no image data and 1 thumbnails>"
    str_heif_img_loaded = "<HeifImage 128x128 RGBA with 65536 bytes image data and 1 thumbnails>"
    str_thumb_not_loaded = "<HeifThumbnail 64x64 RGBA with no image data>"
    str_thumb_loaded = "<HeifThumbnail 64x64 RGBA with 16384 bytes image data>"
    heif_file = pillow_heif.open_heif(Path("images/rgb8_128_128_2_1.heic"))
    assert str(heif_file) == f"<HeifFile with 2 images: ['{str_heif_img_not_loaded}', '{str_heif_img_not_loaded}']>"
    assert str(heif_file[0]) == str_heif_img_not_loaded
    assert str(heif_file.thumbnails[0]) == f"{str_thumb_not_loaded} Original:{str_heif_img_not_loaded}"
    heif_file.load()
    heif_file.thumbnails[0].load()
    assert str(heif_file[0]) == str_heif_img_loaded
    assert str(heif_file.thumbnails[0]) == f"{str_thumb_loaded} Original:{str_heif_img_loaded}"
    heif_file = pillow_heif.HeifFile().add_from_heif(heif_file[0])
    assert str(heif_file) == f"<HeifFile with 1 images: ['{str_heif_img_loaded}']>"
    assert str(heif_file.thumbnails[0]) == f"{str_thumb_not_loaded} Original:{str_heif_img_loaded}"
    heif_file.thumbnails[0].load()  # Should not change anything, thumbnails are cloned without data.
    assert str(heif_file.thumbnails[0]) == f"{str_thumb_not_loaded} Original:{str_heif_img_loaded}"
