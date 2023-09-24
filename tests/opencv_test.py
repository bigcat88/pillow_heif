# With OpenCV, we test BGR, BGRA, BGR;16 and BGRA;16 modes

import os
import sys
from io import BytesIO
from pathlib import Path
from subprocess import CalledProcessError, run

import pytest
from helpers import compare_hashes, hevc_enc
from PIL import Image

from pillow_heif import HeifImagePlugin  # noqa
from pillow_heif import from_bytes, open_heif, options

np = pytest.importorskip("numpy", reason="NumPy not installed")
cv2 = pytest.importorskip("cv2", reason="OpenCV not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("enc_bits", (10, 12))
@pytest.mark.parametrize(
    "img",
    (
        "images/non_heif/RGB_16__29x100.png",
        "images/non_heif/RGB_16__128x128.png",
    ),
)
def test_save_bgr_16bit_to_10_12_bit(enc_bits, img):
    try:
        options.SAVE_HDR_TO_12_BIT = bool(enc_bits == 12)
        cv_img = cv2.imread(img, cv2.IMREAD_UNCHANGED)
        assert cv_img.shape[2] == 3  # 3 channels(BGR)
        heif_file = from_bytes(mode="BGR;16", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
        out_heic = BytesIO()
        heif_file.save(out_heic, quality=-1)
        heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
        assert heif_file.info["bit_depth"] == enc_bits
        png_pillow = Image.open(Path(img))
        heif_pillow = Image.open(out_heic)
        compare_hashes([png_pillow, heif_pillow], hash_size=8)
    finally:
        options.SAVE_HDR_TO_12_BIT = False


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("enc_bits", (10, 12))
@pytest.mark.parametrize(
    "img",
    (
        "images/non_heif/RGBA_16__29x100.png",
        "images/non_heif/RGBA_16__128x128.png",
    ),
)
def test_save_bgra_16bit_to_10_12_bit(enc_bits, img):
    try:
        options.SAVE_HDR_TO_12_BIT = bool(enc_bits == 12)
        cv_img = cv2.imread(img, cv2.IMREAD_UNCHANGED)
        assert cv_img.shape[2] == 4  # 4 channels(BGRA)
        heif_file = from_bytes(mode="BGRA;16", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
        out_heic = BytesIO()
        heif_file.save(out_heic, quality=-1)
        heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
        assert heif_file.info["bit_depth"] == enc_bits
        png_pillow = Image.open(Path(img))
        heif_pillow = Image.open(out_heic)
        compare_hashes([png_pillow, heif_pillow], hash_size=8, max_difference=1)
    finally:
        options.SAVE_HDR_TO_12_BIT = False


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize(
    "img",
    (
        "images/non_heif/RGB_8__29x100.png",
        "images/non_heif/RGB_8__128x128.png",
    ),
)
def test_save_bgr_8bit_color_mode(img):
    cv_img = cv2.imread(img, cv2.IMREAD_UNCHANGED)
    assert cv_img.shape[2] == 3  # 3 channels(BGR)
    heif_file = from_bytes(mode="BGR", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert open_heif(out_heic, convert_hdr_to_8bit=False).info["bit_depth"] == 8
    png_pillow = Image.open(img)
    heif_pillow = Image.open(out_heic)
    compare_hashes([png_pillow, heif_pillow], hash_size=8)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize(
    "img",
    (
        "images/non_heif/RGBA_8__29x100.png",
        "images/non_heif/RGBA_8__128x128.png",
    ),
)
def test_save_bgra_8bit_color_mode(img):
    cv_img = cv2.imread(img, cv2.IMREAD_UNCHANGED)
    assert cv_img.shape[2] == 4  # 4 channels(BGRA)
    heif_file = from_bytes(mode="BGRA", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert open_heif(out_heic, convert_hdr_to_8bit=False).info["bit_depth"] == 8
    png_pillow = Image.open(img)
    heif_pillow = Image.open(out_heic)
    compare_hashes([png_pillow, heif_pillow], hash_size=8)


@pytest.mark.parametrize(
    "img",
    (
        "images/heif/L_8__29x100.heif",
        "images/heif/L_8__128x128.heif",
        "images/heif/L_10__29x100.heif",
        "images/heif/L_10__128x128.heif",
        "images/heif/L_12__29x100.heif",
        "images/heif/L_12__128x128.heif",
        "images/heif/LA_8__29x100.heif",
        "images/heif/LA_8__128x128.heif",
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
def test_read_8_10_12_bit(img):
    heif_file = open_heif(img, convert_hdr_to_8bit=False, bgr_mode=True)
    np_array = np.asarray(heif_file)
    img_encode = cv2.imencode(".png", np_array)[1]
    compare_hashes([BytesIO(img_encode), img], hash_size=24)
    # here we test `decode_image` method from _pillow_heif.c
    path_to_png = "images/non_heif/" + Path(img).name
    path_to_png = path_to_png.replace(".heif", ".png")
    path_to_png = path_to_png.replace("_10_", "_16_")
    path_to_png = path_to_png.replace("_12_", "_16_")
    compare_hashes([BytesIO(img_encode), path_to_png], hash_size=16)


def test_opencv_crash():
    # https://github.com/bigcat88/pillow_heif/issues/89
    path_to_test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "opencv_bug.py")
    if sys.platform.lower() == "darwin":
        with pytest.raises(CalledProcessError):
            run([sys.executable, path_to_test_file], check=True)
    else:
        run([sys.executable, path_to_test_file], check=True)
