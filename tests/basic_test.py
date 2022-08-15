import builtins
import os
import sys
from pathlib import Path

import dataset
import pytest

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def test_libheif_info():
    info = pillow_heif.libheif_info()
    assert info["version"]["libheif"] == "1.12.0"
    assert info["decoders"]["HEVC"]
    if os.getenv("PH_LIGHT", "0") != "0" or sys.maxsize <= 2**32:
        return
    assert info["decoders"]["AV1"]
    assert info["encoders"]["AV1"]
    assert info["encoders"]["HEVC"]


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_get_file_mimetype(img_path):
    mimetype = pillow_heif.get_file_mimetype(img_path)
    assert mimetype in ("image/heic", "image/heic-sequence", "image/heif", "image/heif-sequence", "image/avif")
    assert mimetype == pillow_heif.open_heif(img_path, False).mimetype


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_heif_check_filetype(img_path):
    with builtins.open(img_path, "rb") as fh:
        assert pillow_heif.check_heif(fh) != pillow_heif.HeifFiletype.NO
        assert pillow_heif.is_supported(fh)


def test_is_supported_fails():
    assert not pillow_heif.is_supported(Path("images/non_heif/xmp.jpeg"))


def test_heif_str():
    str_img_nl_1 = "<HeifImage 64x64 RGB with no image data and 2 thumbnails>"
    str_img_nl_2 = "<HeifImage 64x64 RGB with no image data and 1 thumbnails>"
    str_img_nl_3 = "<HeifImage 96x64 RGB with no image data and 0 thumbnails>"
    str_img_l_1 = "<HeifImage 64x64 RGB with 12288 bytes image data and 2 thumbnails>"
    str_img_l_2 = "<HeifImage 64x64 RGB with 12288 bytes image data and 1 thumbnails>"
    str_thumb_nl = "<HeifThumbnail 32x32 RGB with no image data>"
    str_thumb_l = "<HeifThumbnail 32x32 RGB with 6144 bytes image data>"
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    assert str(heif_file) == f"<HeifFile with 3 images: ['{str_img_nl_1}', '{str_img_nl_2}', '{str_img_nl_3}']>"
    assert str(heif_file[0]) == str_img_nl_1
    assert str(heif_file[1]) == str_img_nl_2
    assert str(heif_file[2]) == str_img_nl_3
    assert str(heif_file.thumbnails[0]) == f"{str_thumb_nl} Original:{str_img_nl_2}"
    heif_file.load()
    assert str(heif_file) == f"<HeifFile with 3 images: ['{str_img_nl_1}', '{str_img_l_2}', '{str_img_nl_3}']>"
    heif_file.thumbnails[0].load()
    assert str(heif_file.thumbnails[0]) == f"{str_thumb_l} Original:{str_img_l_2}"
    heif_file = pillow_heif.HeifFile().add_from_heif(heif_file[0])
    assert str(heif_file) == f"<HeifFile with 1 images: ['{str_img_l_1}']>"
    assert str(heif_file.thumbnails[0]) == f"{str_thumb_nl} Original:{str_img_l_1}"
    heif_file.thumbnails[0].load()  # Should not change anything, thumbnails are cloned without data.
    assert str(heif_file.thumbnails[0]) == f"{str_thumb_nl} Original:{str_img_l_1}"
