import builtins
import contextlib
import os
from pathlib import Path

import dataset
import helpers
import pytest

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def test_libheif_info():
    info = pillow_heif.libheif_info()
    for key in ("HEIF", "AVIF", "encoders", "decoders"):
        assert key in info

    version = pillow_heif.libheif_version()
    valid_prefixes = ["1.17.", "1.18.", "1.19.", "1.20."]
    assert any(version.startswith(prefix) for prefix in valid_prefixes)


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_get_file_mimetype(img_path):
    mimetype = pillow_heif.get_file_mimetype(img_path)
    assert mimetype in (
        "image/heic",
        "image/heif",
        "image/heif-sequence",
    )
    assert mimetype == pillow_heif.open_heif(img_path, False).mimetype


def test_get_file_mimetype_avif():
    _ = b"\x00\x00\x00\x1c\x66\x74\x79\x70\x61\x76\x69\x66\x00\x00\x00\x00\x61\x76\x69\x66"
    assert pillow_heif.get_file_mimetype(_) == "image/avif"
    # coverage for HeifFile line: options.PREFERRED_DECODER.get("AVIF", "")
    with contextlib.suppress(ValueError):
        pillow_heif.HeifFile(_)


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
        b"\x00\x00\x00\x24\x66\x74\x79\x70\x68\x65\x69\x5a",
    ),
)
def test_get_file_mimetype_invalid(img):
    assert pillow_heif.get_file_mimetype(img) == ""


@pytest.mark.parametrize("img_path", dataset.FULL_DATASET)
def test_is_supported(img_path):
    with builtins.open(img_path, "rb") as fh:
        assert pillow_heif.is_supported(fh)


@pytest.mark.parametrize(
    "img",
    (
        b"",
        b"\x00\x00\x00\x24",
        b"\x00\x00\x00\x24\x66\x74\x79\x70",
        b"\x00\x00\x00\x24\x66\x74\x79\x70\x68\x65\x69\x5a",
        Path("images/non_heif/xmp.jpeg"),
    ),
)
def test_is_supported_fails(img):
    assert not pillow_heif.is_supported(img)


def test_heif_str():
    str_img_nl_1 = "<HeifImage 64x64 RGB with no image data and 2 thumbnails>"
    str_img_nl_2 = "<HeifImage 64x64 L with no image data and 1 thumbnails>"
    str_img_nl_3 = "<HeifImage 96x64 RGB with no image data and 0 thumbnails>"
    str_img_l_1 = "<HeifImage 64x64 RGB with 12288 bytes image data and 2 thumbnails>"
    str_img_l_2 = "<HeifImage 64x64 L with 4096 bytes image data and 1 thumbnails>"
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    assert str(heif_file) == f"<HeifFile with 3 images: ['{str_img_nl_1}', '{str_img_nl_2}', '{str_img_nl_3}']>"
    assert str(heif_file[0]) == str_img_nl_1
    assert str(heif_file[1]) == str_img_nl_2
    assert str(heif_file[2]) == str_img_nl_3
    assert heif_file.data
    assert str(heif_file) == f"<HeifFile with 3 images: ['{str_img_nl_1}', '{str_img_l_2}', '{str_img_nl_3}']>"
    heif_file2 = pillow_heif.HeifFile()
    heif_file2.add_from_heif(heif_file[0])
    assert str(heif_file2) == f"<HeifFile with 1 images: ['{str_img_l_1}']>"


@pytest.mark.skipif(not helpers.RELEASE_FULL_FLAG, reason="Only when building full release")
def test_full_build():
    info = pillow_heif.libheif_info()
    assert not info["AVIF"]
    assert info["HEIF"]
    assert info["encoders"]
    assert info["decoders"]
    expected_version = os.getenv("EXP_PH_LIBHEIF_VERSION", "1.20.2")
    if expected_version:
        assert info["libheif"] == expected_version


@pytest.mark.skipif(not helpers.RELEASE_LIGHT_FLAG, reason="Only when building light release")
def test_light_build():
    info = pillow_heif.libheif_info()
    assert not info["AVIF"]
    assert not info["HEIF"]
    assert info["decoders"]
    expected_version = os.getenv("EXP_PH_LIBHEIF_VERSION", "1.20.2")
    if expected_version:
        assert info["libheif"] == expected_version


@pytest.mark.skipif(not os.getenv("TEST_PLUGIN_LOAD"), reason="Only when plugins present")
def test_load_plugin():
    pillow_heif.load_libheif_plugin(os.environ["TEST_PLUGIN_LOAD"])
    with pytest.raises(RuntimeError):
        pillow_heif.load_libheif_plugin("invalid path")
