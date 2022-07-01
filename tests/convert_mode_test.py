import os
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from pillow_heif import from_pillow, open_heif, options, register_heif_opener

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


imagehash = pytest.importorskip("compare_hashes", reason="NumPy not installed")
if not options().hevc_enc:
    pytest.skip("No HEVC encoder.", allow_module_level=True)


@pytest.mark.parametrize("mode", ("RGB;16", "BGR;16"))
def test_rgb8_to_16bit_color_mode(mode):
    png_pillow = Image.open(Path("images/jpeg_gif_png/RGB_8.png"))
    heif_file = from_pillow(png_pillow)
    assert heif_file.bit_depth == 8
    heif_file[0].convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert not heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert not heif_file.has_alpha
    imagehash.compare_hashes([png_pillow, out_heic], hash_size=16, max_difference=0)


@pytest.mark.parametrize("mode", ("RGBA;16", "BGRA;16"))
def test_rgba8_to_16bit_color_mode(mode):
    png_pillow = Image.open(Path("images/jpeg_gif_png/RGBA_8.png"))
    heif_file = from_pillow(png_pillow)
    assert heif_file.bit_depth == 8
    heif_file[0].convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert heif_file.has_alpha
    imagehash.compare_hashes([png_pillow, out_heic], hash_size=8, max_difference=0)


@pytest.mark.parametrize("mode", ("RGB;16", "BGR;16"))
def test_rgb10_to_16bit_color_mode(mode):
    img_path = Path("images/rgb10.heif")
    heif_file = open_heif(img_path, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    heif_file[0].convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert not heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert not heif_file.has_alpha
    imagehash.compare_hashes([img_path, out_heic], hash_size=8, max_difference=0)


@pytest.mark.parametrize("mode", ("RGBA;16", "BGRA;16"))
def test_rgba10_to_16bit_color_mode(mode):
    img_path = Path("images/rgba10.heif")
    heif_file = open_heif(img_path, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    heif_file[0].convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert heif_file.has_alpha
    imagehash.compare_hashes([img_path, out_heic], hash_size=8, max_difference=0)


@pytest.mark.parametrize("mode", ("RGB;16", "BGR;16"))
def test_rgb12_to_16bit_color_mode(mode):
    img_path = Path("images/rgb12.heif")
    heif_file = open_heif(img_path, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 12
    heif_file[0].convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert not heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert not heif_file.has_alpha
    imagehash.compare_hashes([img_path, out_heic], hash_size=8, max_difference=0)


@pytest.mark.parametrize("mode", ("RGBA;16", "BGRA;16"))
def test_rgba12_to_16bit_color_mode(mode):
    img_path = Path("images/rgba12.heif")
    heif_file = open_heif(img_path, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 12
    heif_file[0].convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert heif_file.has_alpha
    imagehash.compare_hashes([img_path, out_heic], hash_size=8, max_difference=0)
