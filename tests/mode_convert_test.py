import os
from io import BytesIO
from pathlib import Path

import helpers
import pytest

from pillow_heif import from_pillow, open_heif, options, register_heif_opener

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()

pytest.importorskip("numpy", reason="NumPy not installed")
if not helpers.hevc_enc():
    pytest.skip("No HEVC encoder.", allow_module_level=True)


def test_primary_convert_to():
    im = helpers.gradient_rgb()
    im_heif = from_pillow(im)
    im_heif.add_from_pillow(im)
    im_heif.convert_to("BGR;16")
    assert im_heif[0].mode == "BGR;16"
    assert im_heif[1].mode == "RGB"
    im_heif = from_pillow(im)
    im_heif[0].convert_to("RGB;16")
    assert im_heif.mode == "RGB;16"


def test_convert_to_same_mode():
    im_heif = open_heif(helpers.create_heif())
    assert im_heif.mode == "RGB"
    im_heif.convert_to(im_heif.mode)
    assert im_heif.mode == "RGB"
    # Image should not be loaded, when target mode equal to current.
    assert not getattr(im_heif[0], "_img_data")


@pytest.mark.parametrize("enc_bits", (10, 12))
@pytest.mark.parametrize("mode", ("RGB;16", "BGR;16"))
def test_rgb8_to_16_bit_color_mode(mode, enc_bits):
    try:
        options().save_to_12bit = True if enc_bits == 12 else False
        png_pillow = helpers.gradient_rgb()
        heif_file = from_pillow(png_pillow)
        assert heif_file.bit_depth == 8
        heif_file.convert_to(mode)
        out_heic = BytesIO()
        heif_file.save(out_heic, quality=-1)
        assert heif_file.bit_depth == 16
        assert not heif_file.has_alpha
        heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
        assert heif_file.bit_depth == enc_bits
        assert not heif_file.has_alpha
        helpers.compare_hashes([png_pillow, out_heic], hash_size=8)
    finally:
        options().reset()


@pytest.mark.parametrize("enc_bits", (10, 12))
@pytest.mark.parametrize("mode", ("RGBA;16", "BGRA;16"))
def test_rgba8_to_16_bit_color_mode(mode, enc_bits):
    try:
        options().save_to_12bit = True if enc_bits == 12 else False
        png_pillow = helpers.gradient_rgba()
        heif_file = from_pillow(png_pillow)
        assert heif_file.bit_depth == 8
        heif_file.convert_to(mode)
        out_heic = BytesIO()
        heif_file.save(out_heic, quality=-1)
        assert heif_file.bit_depth == 16
        assert heif_file.has_alpha
        heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
        assert heif_file.bit_depth == enc_bits
        assert heif_file.has_alpha
        helpers.compare_hashes([png_pillow, out_heic], hash_size=8)
    finally:
        options().reset()


@pytest.mark.parametrize("img, bit", (("images/heif/RGB_10.heif", 10), ("images/heif/RGB_12.heif", 12)))
@pytest.mark.parametrize("mode", ("RGB;16", "BGR;16"))
def test_rgb_hdr_to_16bit_color_mode(img, mode, bit):
    heif_file = open_heif(Path(img), convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == bit
    heif_file.convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert not heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert not heif_file.has_alpha
    helpers.compare_hashes([Path(img), out_heic], hash_size=8)


@pytest.mark.parametrize("img, bit", (("images/heif/RGBA_10.heif", 10), ("images/heif/RGBA_12.heif", 12)))
@pytest.mark.parametrize("mode", ("RGBA;16", "BGRA;16"))
def test_rgba_hdr_to_16bit_color_mode(img, mode, bit):
    heif_file = open_heif(Path(img), convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == bit
    heif_file.convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert heif_file.has_alpha
    helpers.compare_hashes([Path(img), out_heic], hash_size=8, max_difference=1)


def test_rgba16_to_rgba_color_mode():
    heif_file_orig = open_heif("images/heif/RGBA_10.heif", convert_hdr_to_8bit=True)
    heif_file = open_heif("images/heif/RGBA_10.heif", convert_hdr_to_8bit=False)
    heif_file.convert_to("RGBA;16")
    heif_file.convert_to("RGBA")
    helpers.assert_image_similar(heif_file.to_pillow(), heif_file_orig.to_pillow())


def test_rgba_premultiplied_to_rgb():
    im_heif = from_pillow(helpers.gradient_rgba().crop((124, 124, 132, 132)))
    im_heif.premultiplied_alpha = True
    assert im_heif.mode == "RGBa"
    im_heif.convert_to("RGB")
    assert im_heif.mode == "RGB"
    assert (
        im_heif.to_pillow().tobytes().hex()
        == "3f3f433f3f423e3f423e3f413d3f413d3f403c3f403c3f3f403f423f3f423f3f413e3f413e3f4"
        "03d3f403d3f3f3c3f3f403f42403f413f3f413f3f403e3f403e3f3f3d3f3f3d3f3e413f41403f"
        "41403f403f3f403f3f3f3e3f3f3e3f3e3d3f3e413f41413f40403f40403f3f3f3f3f3f3f3e3e3"
        "f3e3e3f3d423f40413f40413f3f403f3f403f3e3f3f3e3f3f3d3e3f3d423f40423f3f413f3f41"
        "3f3e403f3e403f3d3f3f3d3f3f3c433f3f423f3f423f3e413f3e413f3d403f3d403f3c3f3f3c"
    )


def test_rgba_premultiplied_to_bgr():
    im_heif = from_pillow(helpers.gradient_rgba().crop((124, 124, 132, 132)))
    im_heif.premultiplied_alpha = True
    assert im_heif.mode == "RGBa"
    im_heif.convert_to("BGR")
    assert im_heif.mode == "BGR"
    im_heif.convert_to("RGB")
    assert (
        im_heif.to_pillow().tobytes().hex()
        == "3f3f433f3f423e3f423e3f413d3f413d3f403c3f403c3f3f403f423f3f423f3f413e3f413e3f4"
        "03d3f403d3f3f3c3f3f403f42403f413f3f413f3f403e3f403e3f3f3d3f3f3d3f3e413f41403f"
        "41403f403f3f403f3f3f3e3f3f3e3f3e3d3f3e413f41413f40403f40403f3f3f3f3f3f3f3e3e3"
        "f3e3e3f3d423f40413f40413f3f403f3f403f3e3f3f3e3f3f3d3e3f3d423f40423f3f413f3f41"
        "3f3e403f3e403f3d3f3f3d3f3f3c433f3f423f3f423f3e413f3e413f3d403f3d403f3c3f3f3c"
    )
