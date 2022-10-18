import builtins
import os
from pathlib import Path

import dataset
import helpers
import pytest

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def test_libheif_info():
    info = pillow_heif.libheif_info()
    assert info["version"]["libheif"] in ("1.12.0", "1.13.0")
    assert info["decoders"]["HEVC"]


@pytest.mark.skipif(helpers.aom_enc() and helpers.aom_dec(), reason="Only when AOM missing.")
@pytest.mark.skipif(pillow_heif.libheif_info()["version"]["aom"] == "Rav1e encoder", reason="Rav1e not supported")
def test_pillow_register_avif_plugin():
    with pytest.warns(UserWarning):
        pillow_heif.register_avif_opener()


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_get_file_mimetype(img_path):
    mimetype = pillow_heif.get_file_mimetype(img_path)
    assert mimetype in (
        "image/heic",
        "image/heif",
        "image/heif-sequence",
        "image/avif",
    )
    assert mimetype == pillow_heif.open_heif(img_path, False).mimetype


def test_get_file_mimetype_not_supported():
    # "ftypavis" - currently `libheif` does not support this mimetype.
    _ = b"\x00\x00\x00\x20\x66\x74\x79\x70\x61\x76\x69\x73"
    assert pillow_heif.get_file_mimetype(_) == "image/avif-sequence"
    # "ftyphevc" - if anyone has a sample with this mimetype, please send me :)
    _ = b"\x00\x00\x00\x20\x66\x74\x79\x70\x68\x65\x76\x78"
    assert pillow_heif.get_file_mimetype(_) == "image/heic-sequence"


@pytest.mark.parametrize(
    "img",
    (
        b"",
        b"\x00\x00\x00\x24\x66\x74\x79\x70",
        b"\x00\x00\x00\x24\x66\x74\x79\x70\x68\x65\x69\x5A",
    ),
)
def test_get_file_mimetype_invalid(img):
    assert pillow_heif.get_file_mimetype(img) == ""


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_heif_check_filetype(img_path):
    with builtins.open(img_path, "rb") as fh:
        assert pillow_heif.check_heif(fh) != pillow_heif.HeifFiletype.NO
        assert pillow_heif.is_supported(fh)


@pytest.mark.parametrize(
    "img",
    (
        b"",
        b"\x00\x00\x00\x24",
        b"\x00\x00\x00\x24\x66\x74\x79\x70",
        b"\x00\x00\x00\x24\x66\x74\x79\x70\x68\x65\x69\x5A",
        Path("images/non_heif/xmp.jpeg"),
    ),
)
def test_is_supported_fails(img):
    assert not pillow_heif.is_supported(img)


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


@pytest.mark.skipif(not helpers.RELEASE_FULL_FLAG, reason="Only when building full release")
def test_full_build():
    info = pillow_heif.libheif_info()
    assert info["decoders"]["AV1"]
    assert info["encoders"]["AV1"]
    assert info["encoders"]["HEVC"]
    assert info["version"]["libheif"] == os.getenv("EXP_PH_LIBHEIF_VERSION", "1.13.0")


@pytest.mark.skipif(not helpers.RELEASE_LIGHT_FLAG, reason="Only when building light release")
def test_light_build():
    info = pillow_heif.libheif_info()
    assert not info["decoders"]["AV1"]
    assert not info["encoders"]["AV1"]
    assert not info["encoders"]["HEVC"]
    assert info["version"]["libheif"] == os.getenv("EXP_PH_LIBHEIF_VERSION", "1.13.0")
