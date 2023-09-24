import builtins
import os
from gc import collect
from io import SEEK_END, BytesIO
from pathlib import Path
from unittest import mock

import helpers
import pytest
from PIL import Image, ImageSequence

import pillow_heif

pytest.importorskip("numpy", reason="NumPy not installed")

if not helpers.hevc_enc() or not helpers.aom():
    pytest.skip("No HEIF or AVIF support.", allow_module_level=True)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pillow_heif.register_avif_opener()
pillow_heif.register_heif_opener()


@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_save_format(save_format):
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format=save_format, quality=1)
    mime = pillow_heif.get_file_mimetype(buf.getbuffer().tobytes())
    assert mime == "image/avif" if save_format == "AVIF" else "image/heic"


@pytest.mark.parametrize(
    "img",
    (
        "images/heif/RGBA_8__29x100.heif",
        "images/heif/RGBA_10__29x100.heif",
        "images/heif/RGBA_12__29x100.heif",
    ),
)
def test_premultiplied_alpha(img):
    heif_file = pillow_heif.open_heif(img, convert_hdr_to_8bit=False)
    assert heif_file.has_alpha
    assert not heif_file.premultiplied_alpha
    heif_file.premultiplied_alpha = True
    assert heif_file.has_alpha
    assert heif_file.premultiplied_alpha
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    out_heif_file = pillow_heif.open_heif(out_heic, convert_hdr_to_8bit=False)
    assert out_heif_file.has_alpha
    assert out_heif_file.premultiplied_alpha
    out_heif_file.premultiplied_alpha = False
    assert out_heif_file.has_alpha
    assert not out_heif_file.premultiplied_alpha
    out_heic.seek(0)
    out_heif_file.save(out_heic, quality=-1)
    out_heif_file = pillow_heif.open_heif(out_heic, convert_hdr_to_8bit=False)
    assert out_heif_file.has_alpha
    assert not out_heif_file.premultiplied_alpha


def test_outputs():
    heif_file = pillow_heif.open_heif(helpers.create_heif((31, 64)))
    output = BytesIO()
    heif_file.save(output, quality=10)
    assert output.seek(0, SEEK_END) > 0
    with builtins.open(Path("tmp.heic"), "wb") as output:
        heif_file.save(output, quality=10)
        assert output.seek(0, SEEK_END) > 0
    heif_file.save(Path("tmp.heic"), quality=10)
    assert Path("tmp.heic").stat().st_size > 0
    Path("tmp.heic").unlink()
    with pytest.raises(TypeError):
        heif_file.save(bytes(b"1234567890"), quality=10)


def test_heif_save_one_all():
    im = pillow_heif.open_heif(helpers.create_heif((61, 64), n_images=2))
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF")
    assert len(pillow_heif.open_heif(out_heif)) == 2
    im.save(out_heif, format="HEIF", save_all=False)
    assert len(pillow_heif.open_heif(out_heif)) == 1


def test_pillow_save_one_all():
    im = Image.open(helpers.create_heif((61, 64), n_images=2))
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF")
    assert len(pillow_heif.open_heif(out_heif)) == 1
    im.save(out_heif, format="HEIF", save_all=True)
    assert len(pillow_heif.open_heif(out_heif)) == 2


def test_heif_no_encoder():
    with mock.patch.dict("pillow_heif.heif._pillow_heif.lib_info", {"libheif": "1.14.2", "HEIF": "", "AVIF": ""}):
        im_heif = pillow_heif.from_pillow(Image.new("L", (64, 64)))
        out_buffer = BytesIO()
        with pytest.raises(RuntimeError):
            im_heif.save(out_buffer)


@pytest.mark.parametrize("size", ((1, 0), (0, 1), (0, 0)))
def test_pillow_save_zero(size: tuple):
    out_heif = BytesIO()
    im = Image.new("RGB", size)
    with pytest.raises(ValueError):
        im.save(out_heif, format="HEIF")


@pytest.mark.parametrize("size", ((1, 0), (0, 1), (0, 0)))
def test_heif_save_zero(size: tuple):
    out_heif = BytesIO()
    im = pillow_heif.from_bytes("L", size, b"")
    with pytest.raises(ValueError):
        im.save(out_heif, format="HEIF")


def test_heif_save_empty():
    heic_file = pillow_heif.open_heif(helpers.create_heif())
    del heic_file[0]
    with pytest.raises(ValueError):
        heic_file.save(BytesIO())


def test_save_empty_with_append():
    out_buffer = BytesIO()
    empty_heif_file = pillow_heif.HeifFile()
    heif_file = pillow_heif.open_heif(helpers.create_heif())
    empty_heif_file.save(out_buffer, append_images=[heif_file[0]])
    helpers.compare_heif_files_fields(heif_file, pillow_heif.open_heif(out_buffer))
    empty_heif_file.save(out_buffer, append_images=[heif_file[0]], save_all=False)
    heif_file = pillow_heif.open_heif(out_buffer)
    assert len(heif_file) == 1


def test_hif_file():
    hif_path = Path("images/heif_other/cat.hif")
    heif_file1 = pillow_heif.open_heif(hif_path)
    assert heif_file1.info["bit_depth"] == 10
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=80)
    heif_file2 = pillow_heif.open_heif(out_buf)
    assert heif_file2.info["bit_depth"] == 8
    helpers.compare_heif_files_fields(heif_file1, heif_file2, ignore=["bit_depth"])
    helpers.compare_hashes([hif_path, out_buf], hash_size=16)


@pytest.mark.parametrize(
    "im_path",
    (
        "images/heif/L_10__29x100",
        "images/heif/L_10__128x128",
        "images/heif/L_12__29x100",
        "images/heif/L_12__128x128",
        "images/heif/RGB_10__29x100",
        "images/heif/RGB_10__128x128",
        "images/heif/RGB_12__29x100",
        "images/heif/RGB_12__128x128",
        "images/heif/RGBA_10__29x100",
        "images/heif/RGBA_10__128x128",
        "images/heif/RGBA_12__29x100",
        "images/heif/RGBA_12__128x128",
    ),
)
@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_hdr_save(im_path, save_format):
    im_path = im_path + (".heif" if save_format == "HEIF" else ".avif")
    heif_file = pillow_heif.open_heif(im_path, convert_hdr_to_8bit=False)
    out_buf = BytesIO()
    heif_file.save(out_buf, quality=-1, format=save_format, chroma=444)
    heif_file_out = pillow_heif.open_heif(out_buf, convert_hdr_to_8bit=False)
    helpers.compare_heif_files_fields(heif_file, heif_file_out)
    helpers.compare_hashes([im_path, out_buf], hash_size=32)


def test_encoder_parameters():
    out_buf1 = BytesIO()
    out_buf2 = BytesIO()
    heif_buf = helpers.create_heif()
    im_heif = pillow_heif.open_heif(heif_buf)
    im_heif.save(out_buf1, enc_params={"x265:ctu": "32", "x265:min-cu-size": "16", "x265:rdLevel": "2"})
    im_heif.save(out_buf2, enc_params={"x265:ctu": 64, "x265:min-cu-size": 8, "x265:rdLevel": 6})
    assert out_buf1.seek(0, SEEK_END) != out_buf2.seek(0, SEEK_END)


def test_pillow_heif_orientation():
    heic_pillow = Image.open(Path("images/heif_other/arrow.heic"))
    out_jpeg = BytesIO()
    heic_pillow.save(out_jpeg, format="JPEG", quality=90)
    helpers.compare_hashes([heic_pillow, out_jpeg])


def test_pillow_quality():
    heif_original = helpers.create_heif(quality=100)
    im = Image.open(heif_original)
    out_heic_q30 = BytesIO()
    out_heic_q20 = BytesIO()
    im.save(out_heic_q30, format="HEIF", quality=50)
    im.save(out_heic_q20, format="HEIF", quality=20)
    helpers.compare_hashes([im, out_heic_q30, out_heic_q20], hash_size=8, max_difference=2)
    assert out_heic_q20.seek(0, SEEK_END) < out_heic_q30.seek(0, SEEK_END)
    assert out_heic_q30.seek(0, SEEK_END) < heif_original.seek(0, SEEK_END)


@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_P_color_mode(save_format):  # noqa
    im_buffer = BytesIO(helpers.gradient_p_bytes(im_format="TIFF"))
    out_heic = BytesIO()
    im = Image.open(im_buffer)
    im.save(out_heic, format=save_format, quality=90)
    im_heif = Image.open(out_heic)
    assert im_heif.mode == "RGB"
    helpers.compare_hashes([im_buffer, im_heif], hash_size=16)


@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_PA_color_mode(save_format):  # noqa
    im_buffer = BytesIO(helpers.gradient_pa_bytes(im_format="TIFF"))
    out_heic = BytesIO()
    im = Image.open(im_buffer)
    im.save(out_heic, format=save_format, quality=90)
    im_heif = Image.open(out_heic)
    assert im_heif.mode == "RGBA"
    helpers.compare_hashes([im_buffer, im_heif], hash_size=16)


@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_L_color_mode(save_format):  # noqa
    im = Image.linear_gradient(mode="L")
    out_heif = BytesIO()
    im.save(out_heif, format=save_format, quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGB"
    helpers.compare_hashes([im, im_heif], hash_size=32)


@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_LA_color_mode(save_format):  # noqa
    im = Image.open(BytesIO(helpers.gradient_la_bytes(im_format="PNG")))
    out_heif = BytesIO()
    im.save(out_heif, format=save_format, quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGBA"
    helpers.compare_hashes([im, im_heif], hash_size=32)


def test_1_color_mode():
    im = Image.linear_gradient(mode="L")
    im = im.convert(mode="1")
    assert im.mode == "1"
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF", quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGB"
    helpers.compare_hashes([im, im_heif], hash_size=16)


def test_CMYK_color_mode():  # noqa
    im = helpers.gradient_rgba().convert("CMYK")
    assert im.mode == "CMYK"
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF", quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGBA"
    helpers.compare_hashes([im, im_heif], hash_size=16)


def test_YCbCr_color_mode():  # noqa
    im = helpers.gradient_rgb().convert("YCbCr")
    assert im.mode == "YCbCr"
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF", quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGB"
    helpers.compare_hashes([im, im_heif], hash_size=16)


@pytest.mark.parametrize("enc_bits", (10, 12))
@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_I_color_modes_to_10_12_bit(enc_bits, save_format):  # noqa
    try:
        pillow_heif.options.SAVE_HDR_TO_12_BIT = bool(enc_bits == 12)
        src_pillow = Image.open(Path("images/non_heif/L_16__29x100.png"))
        assert src_pillow.mode == "I"
        for mode in ("I", "I;16", "I;16L"):
            i_mode_img = src_pillow.convert(mode=mode)
            out_heic = BytesIO()
            i_mode_img.save(out_heic, format=save_format, quality=-1)
            assert pillow_heif.open_heif(out_heic, convert_hdr_to_8bit=False).info["bit_depth"] == enc_bits
            heic_pillow = Image.open(out_heic)
            helpers.compare_hashes([src_pillow, heic_pillow], hash_size=8)
    finally:
        pillow_heif.options.SAVE_HDR_TO_12_BIT = False


def test_gif():
    # convert first frame of gif
    gif_pillow = Image.open(Path("images/non_heif/chi.gif"))
    out_heic = BytesIO()
    gif_pillow.save(out_heic, format="HEIF")
    helpers.compare_hashes([gif_pillow, out_heic])
    # save second gif frame
    ImageSequence.Iterator(gif_pillow)[1].save(out_heic, format="HEIF")
    helpers.compare_hashes([gif_pillow, out_heic])
    # convert all frames of gif(pillow_heif does not skip identical frames and saves all frames like in source)
    out_all_heic = BytesIO()
    gif_pillow.save(out_all_heic, format="HEIF", save_all=True, quality=80)
    assert out_heic.seek(0, SEEK_END) * 2 < out_all_heic.seek(0, SEEK_END)
    heic_pillow = Image.open(out_all_heic)
    for i, frame in enumerate(ImageSequence.Iterator(gif_pillow)):
        # On Ubuntu 22.04 with basic repos(old versions of libs) without `max_difference` it fails.
        helpers.compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame], max_difference=1)


def test_pillow_append_images():
    im_pil1 = Image.open("images/heif/L_8__29x100.heif")
    im_pil2 = Image.open("images/heif/RGB_8__128x128.heif")
    im_pil3 = Image.open("images/non_heif/RGBA_8__29x100.png")
    im_pil1.info["thumbnails"] = [16]
    im_pil2.info["thumbnails"] = [32]
    im_pil3.info["thumbnails"] = [64]
    out_buf = BytesIO()
    im_pil1.save(out_buf, append_images=[im_pil2, im_pil3], format="HEIF", save_all=True, quality=-1)
    out_heif = Image.open(out_buf)
    assert len([True for _ in ImageSequence.Iterator(out_heif)]) == 3
    assert ImageSequence.Iterator(out_heif)[0].info["thumbnails"] == [16]
    assert ImageSequence.Iterator(out_heif)[1].info["thumbnails"] == [32]
    assert ImageSequence.Iterator(out_heif)[2].info["thumbnails"] == [64]
    helpers.compare_hashes([ImageSequence.Iterator(out_heif)[0], im_pil1], hash_size=24)
    helpers.compare_hashes([ImageSequence.Iterator(out_heif)[1], im_pil2], hash_size=24)
    helpers.compare_hashes([ImageSequence.Iterator(out_heif)[2], im_pil3], hash_size=24)


def test_add_from():
    heif_file1 = pillow_heif.open_heif("images/heif/L_8__29x100.heif")
    heif_file2 = pillow_heif.open_heif("images/heif/RGB_8__128x128.heif")
    im_pil3 = Image.open("images/non_heif/RGBA_8__29x100.png")
    heif_file1.add_from_heif(heif_file2[0])
    heif_file1.add_from_pillow(im_pil3)
    heif_file1[0].info["thumbnails"].append(16)
    heif_file1[1].info["thumbnails"].append(32)
    heif_file1[2].info["thumbnails"].append(64)
    assert not heif_file2.info["thumbnails"]
    heif_file2.info["thumbnails"].append(32)
    collect()
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=-1, chroma=444)
    out_heif = pillow_heif.open_heif(out_buf)
    assert len(out_heif) == 3
    assert out_heif.info["thumbnails"] == [16]
    assert out_heif[1].info["thumbnails"] == [32]
    assert out_heif[2].info["thumbnails"] == [64]
    helpers.compare_heif_files_fields(out_heif[0], heif_file1[0])
    helpers.compare_heif_files_fields(out_heif[1], heif_file2[0])
    helpers.compare_heif_to_pillow_fields(out_heif[2], im_pil3)


def test_remove():
    out_buffer = BytesIO()
    # removing first image
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    del heif_file[0]
    heif_file.save(out_buffer)
    _ = pillow_heif.open_heif(out_buffer)
    assert len(_) == 2
    assert len(_.info["thumbnails"]) == 1
    # removing second and first image
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    del heif_file[1]
    del heif_file[0]
    heif_file.save(out_buffer)
    _ = pillow_heif.open_heif(out_buffer)
    assert len(_) == 1
    assert len(_.info["thumbnails"]) == 0


def test_heif_save_multi_frame():
    heif_file = pillow_heif.open_heif(Path("images/heif_other/nokia/alpha.heic"), convert_hdr_to_8bit=False)
    heif_buf = BytesIO()
    heif_file.save(heif_buf, quality=-1)
    out_heif_file = pillow_heif.open_heif(heif_buf, convert_hdr_to_8bit=False)
    for i in range(3):
        assert heif_file[i].size == out_heif_file[i].size
        assert heif_file[i].mode == out_heif_file[i].mode
        assert heif_file[i].info["bit_depth"] == out_heif_file[i].info["bit_depth"]
        assert heif_file[i].info["primary"] == out_heif_file[i].info["primary"]


def test_pillow_save_multi_frame():
    im = Image.open(Path("images/heif_other/nokia/alpha.heic"))
    heif_buf = BytesIO()
    im.save(heif_buf, format="HEIF", quality=-1, save_all=True)
    out_im = Image.open(heif_buf)
    for i in range(3):
        im.seek(i)
        out_im.seek(i)
        assert im.size == out_im.size
        assert im.mode == out_im.mode
        assert im.info["primary"] == out_im.info["primary"]
        helpers.compare_hashes([im, out_im], hash_size=8)


@pytest.mark.parametrize("chroma, diff_epsilon", ((420, 1.83), (422, 1.32), (444, 0.99)))
@pytest.mark.parametrize("im", (helpers.gradient_rgb(), helpers.gradient_rgba()))
def test_chroma_heif_encoding_8bit(chroma, diff_epsilon, im):
    im_buf = BytesIO()
    im.save(im_buf, format="HEIF", quality=-1, chroma=chroma)
    im_out = Image.open(im_buf)
    im = im.convert(mode=im_out.mode)
    helpers.assert_image_similar(im, im_out, diff_epsilon)


@pytest.mark.parametrize("chroma, diff_epsilon", ((420, 1.83), (422, 1.32), (444, 0.99)))
@pytest.mark.parametrize("im", (helpers.gradient_rgb(), helpers.gradient_rgba()))
def test_chroma_avif_encoding_8bit(chroma, diff_epsilon, im):
    im_buf = BytesIO()
    im.save(im_buf, format="AVIF", quality=-1, chroma=chroma)
    im_out = Image.open(im_buf)
    im = im.convert(mode=im_out.mode)
    helpers.assert_image_similar(im, im_out, diff_epsilon)


@pytest.mark.parametrize("size", ((8, 8), (9, 9), (10, 10), (11, 11), (21, 21), (31, 31), (64, 64)))
@pytest.mark.parametrize("mode", ("L", "LA", "RGB", "RGBA"))
def test_encode_function(mode, size: tuple):
    im = Image.effect_mandelbrot(size, (-3, -2.5, 2, 2.5), 100)
    im = im.convert(mode)
    buf = BytesIO()
    pillow_heif.encode(im.mode, im.size, im.tobytes(), buf, quality=-1)
    helpers.compare_hashes([buf, im])


@pytest.mark.parametrize("mode", ("L", "LA", "RGB", "RGBA"))
def test_encode_function_with_stride(mode):
    im = Image.effect_mandelbrot((512, 512), (-3, -2.5, 2, 2.5), 100)
    im = im.convert(mode)
    buf = BytesIO()
    pillow_heif.encode(im.mode, (257, im.size[1]), im.tobytes(), buf, quality=-1, stride=512 * len(mode))
    im = im.crop((0, 0, 257, 512))
    helpers.compare_hashes([buf, im], hash_size=32)


@pytest.mark.parametrize("mode", ("L", "LA", "RGB", "RGBA", "L;16", "LA;16", "RGB;16", "RGBA;16"))
def test_encode_function_not_enough_data(mode):
    buf = BytesIO()
    with pytest.raises(ValueError):
        pillow_heif.encode(mode, (128, 128), b"123456", buf)


@pytest.mark.parametrize(
    "image_path",
    (
        "images/heif_special/L_8__29(255)x100.heif",
        "images/heif_special/L_8__29x100(255).heif",
        "images/heif_special/L_8__29x100(100x29).heif",
    ),
)
def test_invalid_ispe_stride(image_path):
    im = pillow_heif.read_heif(image_path)
    buf = BytesIO()
    pillow_heif.encode(im.mode, im.size, im.data, buf)
    im = pillow_heif.open_heif(buf)
    assert im.size == (29, 100)


@pytest.mark.parametrize(
    "image_path",
    (
        "images/heif_special/L_8__29(255)x100.heif",
        "images/heif_special/L_8__29x100(255).heif",
        "images/heif_special/L_8__29x100(100x29).heif",
    ),
)
@mock.patch("pillow_heif.options.ALLOW_INCORRECT_HEADERS", True)
def test_invalid_ispe_stride_pillow(image_path):
    im = Image.open(image_path)
    buf = BytesIO()
    im.save(buf, format="HEIF")
    im = Image.open(buf)
    assert im.size == (29, 100)


def test_nclx_profile_write():
    im_rgb = helpers.gradient_rgb()
    buf = BytesIO()
    im_rgb.save(buf, format="HEIF", save_nclx_profile=False)
    assert "nclx_profile" not in Image.open(buf).info
    im_rgb.save(buf, format="HEIF", save_nclx_profile=True)
    assert "nclx_profile" in Image.open(buf).info
    try:
        pillow_heif.options.SAVE_NCLX_PROFILE = True
        im_rgb.save(buf, format="HEIF", save_nclx_profile=False)
        assert "nclx_profile" not in Image.open(buf).info
        im_rgb.save(buf, format="HEIF")
        assert "nclx_profile" in Image.open(buf).info
        im_rgb.info["nclx_profile"] = {
            "color_primaries": 1,
            "transfer_characteristics": 1,
            "matrix_coefficients": 10,
            "full_range_flag": 0,
        }
        im_rgb.save(buf, format="HEIF")
        nclx_out = Image.open(buf).info["nclx_profile"]
        for k in im_rgb.info["nclx_profile"]:
            assert im_rgb.info["nclx_profile"][k] == nclx_out[k]
    finally:
        pillow_heif.options.SAVE_NCLX_PROFILE = False
