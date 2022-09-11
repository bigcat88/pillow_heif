# With OpenCV we test BGR, BGRA, BGR;15 and BGRA;16 modes

import os
from io import BytesIO
from pathlib import Path

import pytest
from helpers import compare_hashes, gradient_rgb_bytes, gradient_rgba_bytes, hevc_enc
from PIL import Image

from pillow_heif import HeifImagePlugin  # noqa
from pillow_heif import from_bytes, open_heif, options

np = pytest.importorskip("numpy", reason="NumPy not installed")
cv2 = pytest.importorskip("cv2", reason="OpenCV not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("enc_bits", (10, 12))
def test_save_bgr_16bit_to_10_12_bit(enc_bits):
    try:
        options().save_to_12bit = True if enc_bits == 12 else False
        image_path = "images/non_heif/RGB_16.png"
        cv_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        assert cv_img.shape[2] == 3  # 3 channels(BGR)
        heif_file = from_bytes(mode="BGR;16", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
        out_heic = BytesIO()
        heif_file.save(out_heic, quality=-1)
        heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
        assert heif_file.bit_depth == enc_bits
        png_pillow = Image.open(Path(image_path))
        heif_pillow = Image.open(out_heic)
        compare_hashes([png_pillow, heif_pillow], hash_size=8)
    finally:
        options().reset()


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("enc_bits", (10, 12))
def test_save_bgra_16bit_to_10_12_bit(enc_bits):
    try:
        options().save_to_12bit = True if enc_bits == 12 else False
        image_path = "images/non_heif/RGBA_16.png"
        cv_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        assert cv_img.shape[2] == 4  # 4 channels(BGRA)
        heif_file = from_bytes(mode="BGRA;16", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
        out_heic = BytesIO()
        heif_file.save(out_heic, quality=-1)
        heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
        assert heif_file.bit_depth == enc_bits
        png_pillow = Image.open(Path(image_path))
        heif_pillow = Image.open(out_heic)
        compare_hashes([png_pillow, heif_pillow], hash_size=8, max_difference=1)
    finally:
        options().reset()


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
def test_save_bgr_8bit_color_mode():
    rgb8_buf = gradient_rgb_bytes("PNG")
    cv_img = cv2.imdecode(np.asarray(rgb8_buf), cv2.IMREAD_UNCHANGED)
    assert cv_img.shape[2] == 3  # 3 channels(BGR)
    heif_file = from_bytes(mode="BGR", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert open_heif(out_heic, convert_hdr_to_8bit=False).bit_depth == 8
    png_pillow = Image.open(BytesIO(rgb8_buf))
    heif_pillow = Image.open(out_heic)
    compare_hashes([png_pillow, heif_pillow], hash_size=8)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
def test_save_bgra_8bit_color_mode():
    rgba8_buf = gradient_rgba_bytes("PNG")
    cv_img = cv2.imdecode(np.asarray(rgba8_buf), cv2.IMREAD_UNCHANGED)
    assert cv_img.shape[2] == 4  # 4 channels(BGRA)
    heif_file = from_bytes(mode="BGRA", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert open_heif(out_heic, convert_hdr_to_8bit=False).bit_depth == 8
    png_pillow = Image.open(BytesIO(rgba8_buf))
    heif_pillow = Image.open(out_heic)
    compare_hashes([png_pillow, heif_pillow], hash_size=8)


@pytest.mark.parametrize(
    "img_path",
    (
        "images/heif/RGB_10.heif",
        "images/heif/RGBA_10.heif",
        "images/heif/RGB_12.heif",
        "images/heif/RGBA_12.heif",
    ),
)
def test_read_10_12_bit(img_path):
    image_path = Path(img_path)
    heif_file = open_heif(image_path, convert_hdr_to_8bit=False)
    heif_file.convert_to("BGRA;16" if heif_file.has_alpha else "BGR;16")
    np_array = np.asarray(heif_file)
    img_encode = cv2.imencode(".png", np_array)[1]
    compare_hashes([BytesIO(img_encode), image_path], hash_size=8)
