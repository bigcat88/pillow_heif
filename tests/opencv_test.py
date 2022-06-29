# With OpenCV we test BGR, BGRA, BGR;15 and BGRA;16 modes

import os
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from pillow_heif import from_bytes, open_heif, options, register_heif_opener

if not options().hevc_enc:
    pytest.skip("No HEVC encoder.", allow_module_level=True)

imagehash = pytest.importorskip("compare_hashes", reason="NumPy not installed")
cv2 = pytest.importorskip("cv2", reason="OpenCV not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


def test_save_bgr_16bit_color_mode():
    image_path = "images/jpeg_gif_png/RGB_16.png"
    cv_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    assert cv_img.shape[2] == 3  # 3 channels(BGR)
    heif_file = from_bytes(mode="BGR;16", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert open_heif(out_heic, convert_hdr_to_8bit=False).bit_depth == 10
    png_pillow = Image.open(Path(image_path))
    heif_pillow = Image.open(out_heic)
    imagehash.compare_hashes([png_pillow, heif_pillow], hash_type="dhash", hash_size=8, max_difference=0)


def test_save_bgra_16bit_color_mode():
    image_path = "images/jpeg_gif_png/RGBA_16.png"
    cv_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    assert cv_img.shape[2] == 4  # 4 channels(BGRA)
    heif_file = from_bytes(mode="BGRA;16", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert open_heif(out_heic, convert_hdr_to_8bit=False).bit_depth == 10
    png_pillow = Image.open(Path(image_path))
    heif_pillow = Image.open(out_heic)
    imagehash.compare_hashes([png_pillow, heif_pillow], hash_type="dhash", hash_size=8, max_difference=1)


def test_save_bgr_8bit_color_mode():
    image_path = "images/jpeg_gif_png/RGB_8.png"
    cv_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    assert cv_img.shape[2] == 3  # 3 channels(BGR)
    heif_file = from_bytes(mode="BGR", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert open_heif(out_heic, convert_hdr_to_8bit=False).bit_depth == 8
    png_pillow = Image.open(Path(image_path))
    heif_pillow = Image.open(out_heic)
    imagehash.compare_hashes([png_pillow, heif_pillow], hash_type="dhash", hash_size=8, max_difference=0)


def test_save_bgra_8bit_color_mode():
    image_path = "images/jpeg_gif_png/RGBA_8.png"
    cv_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    assert cv_img.shape[2] == 4  # 4 channels(BGRA)
    heif_file = from_bytes(mode="BGRA", size=(cv_img.shape[1], cv_img.shape[0]), data=bytes(cv_img))
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert open_heif(out_heic, convert_hdr_to_8bit=False).bit_depth == 8
    png_pillow = Image.open(Path(image_path))
    heif_pillow = Image.open(out_heic)
    imagehash.compare_hashes([png_pillow, heif_pillow], hash_type="dhash", hash_size=8, max_difference=0)
