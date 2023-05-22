import os
from io import BytesIO

import pytest
from helpers import compare_hashes, compare_heif_files_fields, hevc_enc
from PIL import Image

from pillow_heif import HeifImagePlugin  # noqa
from pillow_heif import from_bytes, open_heif

np = pytest.importorskip("numpy", reason="NumPy not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize(
    "img,expected_mode",
    (
        ("images/heif/RGB_8__29x100.heif", "BGR"),
        ("images/heif/RGB_10__29x100.heif", "BGR;16"),
        ("images/heif/RGB_12__29x100.heif", "BGR;16"),
        ("images/heif/RGBA_8__29x100.heif", "BGRA"),
        ("images/heif/RGBA_10__29x100.heif", "BGRA;16"),
        ("images/heif/RGBA_12__29x100.heif", "BGRA;16"),
    ),
)
def test_open_heif(img, expected_mode):
    im = open_heif(img, convert_hdr_to_8bit=False, bgr_mode=True)
    assert im.mode == expected_mode


@pytest.mark.parametrize(
    "img,expected_mode",
    (
        ("images/heif/RGB_8__29x100.heif", "BGR"),
        ("images/heif/RGB_10__29x100.heif", "BGR;10"),
        ("images/heif/RGB_12__29x100.heif", "BGR;12"),
        ("images/heif/RGBA_8__29x100.heif", "BGRA"),
        ("images/heif/RGBA_10__29x100.heif", "BGRA;10"),
        ("images/heif/RGBA_12__29x100.heif", "BGRA;12"),
    ),
)
def test_open_heif_bgr_mode_disable_16bit(img, expected_mode):
    im = open_heif(img, convert_hdr_to_8bit=False, bgr_mode=True, hdr_to_16bit=False)
    assert im.mode == expected_mode


@pytest.mark.parametrize(
    "img,expected_mode",
    (
        ("images/heif/RGB_8__29x100.heif", "RGB"),
        ("images/heif/RGB_10__29x100.heif", "RGB;10"),
        ("images/heif/RGB_12__29x100.heif", "RGB;12"),
        ("images/heif/RGBA_8__29x100.heif", "RGBA"),
        ("images/heif/RGBA_10__29x100.heif", "RGBA;10"),
        ("images/heif/RGBA_12__29x100.heif", "RGBA;12"),
    ),
)
def test_open_heif_disable_16bit(img, expected_mode):
    im = open_heif(img, convert_hdr_to_8bit=False, hdr_to_16bit=False)
    assert im.mode == expected_mode


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize(
    "img",
    (
        "images/heif/RGB_8__29x100.heif",
        "images/heif/RGB_8__128x128.heif",
        "images/heif/RGB_10__29x100.heif",
        "images/heif/RGB_10__128x128.heif",
        "images/heif/RGB_12__29x100.heif",
        "images/heif/RGB_12__128x128.heif",
        "images/heif/RGBA_8__29x100.heif",
        "images/heif/RGBA_8__128x128.heif",
        "images/heif/RGBA_10__29x100.heif",
        "images/heif/RGBA_10__128x128.heif",
        "images/heif/RGBA_12__29x100.heif",
        "images/heif/RGBA_12__128x128.heif",
    ),
)
def test_open_heif_compare_non_standard_modes_data(img):
    im_info = open_heif(img)
    im_pillow = Image.open(img)
    # =======
    rgb = open_heif(img, convert_hdr_to_8bit=False)
    rgb_stride = open_heif(img, convert_hdr_to_8bit=False, remove_stride=False)
    assert rgb.mode == rgb_stride.mode
    np__rgb = np.asarray(rgb)
    np__rgb_stride = np.asarray(rgb_stride)[:, : im_info.size[0], :]
    np.testing.assert_array_equal(np__rgb, np__rgb_stride)
    # =======
    rgb_no16 = open_heif(img, convert_hdr_to_8bit=False, hdr_to_16bit=False)
    rgb_no16_stride = open_heif(img, convert_hdr_to_8bit=False, hdr_to_16bit=False, remove_stride=False)
    assert rgb_no16.mode == rgb_no16_stride.mode
    np__rgb_no16 = np.asarray(rgb_no16)
    np__rgb_no16_stride = np.asarray(rgb_no16_stride)[:, : im_info.size[0], :]
    np.testing.assert_array_equal(np__rgb_no16, np__rgb_no16_stride)
    # =======
    bgr = open_heif(img, convert_hdr_to_8bit=False, bgr_mode=True)
    bgr_stride = open_heif(img, convert_hdr_to_8bit=False, bgr_mode=True, remove_stride=False)
    assert bgr.mode == bgr_stride.mode
    np__bgr = np.asarray(bgr)
    np__bgr_stride = np.asarray(bgr_stride)[:, : im_info.size[0], :]
    np.testing.assert_array_equal(np__bgr, np__bgr_stride)
    # =======
    bgr_no16 = open_heif(img, convert_hdr_to_8bit=False, bgr_mode=True, hdr_to_16bit=False)
    bgr_no16_stride = open_heif(img, convert_hdr_to_8bit=False, bgr_mode=True, hdr_to_16bit=False, remove_stride=False)
    assert bgr_no16.mode == bgr_no16_stride.mode
    np__bgr_no16 = np.asarray(bgr_no16)
    np__bgr_no16_stride = np.asarray(bgr_no16_stride)[:, : im_info.size[0], :]
    np.testing.assert_array_equal(np__bgr_no16, np__bgr_no16_stride)
    # encode test
    buf = BytesIO()
    for i in (rgb, rgb_stride, rgb_no16, rgb_no16_stride, bgr, bgr_stride, bgr_no16, bgr_no16_stride):
        _ = from_bytes(i.mode, i.size, i.data, stride=i.stride)
        _.save(buf, chroma=444, quality=-1)
        compare_hashes([Image.open(buf), im_pillow], hash_size=24)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize(
    "img",
    (
        "images/heif/L_10__29x100.heif",
        "images/heif/L_10__128x128.heif",
        "images/heif/L_12__29x100.heif",
        "images/heif/L_12__128x128.heif",
        "images/heif/RGB_10__29x100.heif",
        "images/heif/RGB_10__128x128.heif",
        "images/heif/RGB_12__29x100.heif",
        "images/heif/RGB_12__128x128.heif",
        "images/heif/RGBA_10__29x100.heif",
        "images/heif/RGBA_10__128x128.heif",
        "images/heif/RGBA_12__29x100.heif",
        "images/heif/RGBA_12__128x128.heif",
    ),
)
@pytest.mark.parametrize("remove_stride", (True, False))
def test_open_save_disable_16bit(img, remove_stride):
    im = open_heif(img, convert_hdr_to_8bit=False, hdr_to_16bit=False, remove_stride=remove_stride)
    buf = BytesIO()
    im.save(buf)
    im_out = open_heif(buf, convert_hdr_to_8bit=False, hdr_to_16bit=False, remove_stride=remove_stride)
    compare_heif_files_fields(im, im_out)
