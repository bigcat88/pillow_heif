import builtins
import math
import os
import zlib
from gc import collect
from io import SEEK_END, BytesIO
from pathlib import Path
from unittest import mock

import helpers
import pytest
from PIL import Image, ImageDraw, ImageSequence

import pillow_heif

pytest.importorskip("numpy", reason="NumPy not installed")

if not helpers.hevc_enc():
    pytest.skip("No HEIF support.", allow_module_level=True)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pillow_heif.register_heif_opener()


@pytest.mark.parametrize("save_format", ("HEIF",))
def test_save_format(save_format):
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format=save_format, quality=1)
    mime = pillow_heif.get_file_mimetype(buf.getbuffer().tobytes())
    assert mime == "image/heic"


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
    def get_lib_info():
        return {"libheif": "1.17.5", "HEIF": "", "AVIF": "", "encoders": {}, "decoders": {}}

    with mock.patch("pillow_heif.heif._pillow_heif.get_lib_info", side_effect=get_lib_info):
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
    heif_file1.save(out_buf, quality=90)
    heif_file2 = pillow_heif.open_heif(out_buf)
    assert heif_file2.info["bit_depth"] == 8
    assert heif_file1.info["nclx_profile"] == heif_file2.info["nclx_profile"]
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
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_hdr_save(im_path, save_format):
    im_path = im_path + ".heif"
    heif_file = pillow_heif.open_heif(im_path, convert_hdr_to_8bit=False)
    out_buf = BytesIO()
    heif_file.save(out_buf, quality=-1, format=save_format, chroma=444)
    heif_file_out = pillow_heif.open_heif(out_buf, convert_hdr_to_8bit=False)
    helpers.compare_heif_files_fields(heif_file, heif_file_out)
    helpers.compare_hashes([im_path, out_buf], hash_size=16)  # was 32 before libheif 1.19 version


def test_encoder_parameters():
    out_buf1 = BytesIO()
    out_buf2 = BytesIO()
    heif_buf = helpers.create_heif()
    im_heif = pillow_heif.open_heif(heif_buf)
    im_heif.save(out_buf1, enc_params={"x265:ctu": "32", "x265:min-cu-size": "16"})
    im_heif.save(out_buf2, enc_params={"x265:ctu": 64, "x265:min-cu-size": 8})
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


@pytest.mark.parametrize("save_format", ("HEIF",))
def test_P_color_mode(save_format):  # noqa
    im_buffer = BytesIO(helpers.gradient_p_bytes(im_format="TIFF"))
    out_heic = BytesIO()
    im = Image.open(im_buffer)
    im.save(out_heic, format=save_format, quality=90)
    im_heif = Image.open(out_heic)
    assert im_heif.mode == "RGB"
    helpers.compare_hashes([im_buffer, im_heif], hash_size=16)


@pytest.mark.parametrize("save_format", ("HEIF",))
def test_PA_color_mode(save_format):  # noqa
    im_buffer = BytesIO(helpers.gradient_pa_bytes(im_format="TIFF"))
    out_heic = BytesIO()
    im = Image.open(im_buffer)
    im.save(out_heic, format=save_format, quality=90)
    im_heif = Image.open(out_heic)
    assert im_heif.mode == "RGBA"
    helpers.compare_hashes([im_buffer, im_heif], hash_size=16)


@pytest.mark.parametrize("save_format", ("HEIF",))
def test_L_color_mode(save_format):  # noqa
    im = Image.linear_gradient(mode="L")
    out_heif = BytesIO()
    im.save(out_heif, format=save_format, quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "L"
    helpers.compare_hashes([im, im_heif], hash_size=32)


@pytest.mark.parametrize("save_format", ("HEIF",))
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
    assert im_heif.mode == "L"
    helpers.compare_hashes([im, im_heif], hash_size=16)


def test_CMYK_color_mode():  # noqa
    im = helpers.gradient_rgba().convert("CMYK")
    assert im.mode == "CMYK"
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF", quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGBA"
    helpers.compare_hashes([im, im_heif], hash_size=16)


@pytest.mark.parametrize("subsampling, expected_max_difference", (("4:4:4", 0.0004), ("4:2:2", 0.11), ("4:2:0", 1.4)))
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_YCbCr_color_mode(
    save_format,
    subsampling,
    expected_max_difference,
):
    im_original = helpers.gradient_rgb()
    buf_jpeg = BytesIO()
    im_original.save(buf_jpeg, format="JPEG", subsampling=subsampling, quality=-1)
    im_jpeg = Image.open(buf_jpeg)
    im_jpeg.draft("YCbCr", im_jpeg.size)
    im_jpeg.load()
    assert im_jpeg.mode == "YCbCr"
    buf_heif = BytesIO()
    im_jpeg.save(buf_heif, format=save_format, subsampling=subsampling, quality=-1)
    im_heif = Image.open(buf_heif)
    assert im_heif.mode == "RGB"
    helpers.assert_image_similar(Image.open(buf_jpeg), im_heif, expected_max_difference)


def test_heif_YCbCr_color_mode():  # noqa
    # we support YCbCr for PIL only.
    # in this test case, the image will be converted to "RGB" during "from_pillow".
    im = helpers.gradient_rgb().convert("YCbCr")
    assert im.mode == "YCbCr"
    im_heif = pillow_heif.from_pillow(im)
    assert im_heif.mode == "RGB"
    out_heif = BytesIO()
    im_heif.save(out_heif, format="HEIF", quality=-1)
    im_out = Image.open(out_heif)
    assert im_out.mode == "RGB"
    helpers.compare_hashes([im, im_out], hash_size=32)


@pytest.mark.parametrize("enc_bits", (10, 12))
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_I_color_modes_to_10_12_bit(enc_bits, save_format):  # noqa
    try:
        pillow_heif.options.SAVE_HDR_TO_12_BIT = bool(enc_bits == 12)
        src_pillow = Image.open(Path("images/non_heif/L_16__29x100.png"))
        assert src_pillow.mode in ("I", "I;16")  # Pillow 10.3+ will open in `I;16`
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
    # PNG has no NCLX; the saved HEIF gets sRGB defaults (#365).
    # compare_heif_to_pillow_fields checks nclx_profile equality, so verify manually.
    assert out_heif[2].size == im_pil3.size
    assert out_heif[2].mode == im_pil3.mode
    nclx = out_heif[2].info["nclx_profile"]
    assert nclx["color_primaries"] == 1
    assert nclx["transfer_characteristics"] == 13
    assert nclx["matrix_coefficients"] == 6


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
    im_buf_subsampling = BytesIO()
    subsampling_map = {
        444: "4:4:4",
        422: "4:2:2",
        420: "4:2:0",
    }
    im.save(im_buf_subsampling, format="HEIF", quality=-1, subsampling=subsampling_map[chroma])
    assert im_buf.getbuffer().nbytes == im_buf_subsampling.getbuffer().nbytes  # results should be the same


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


def test_nclx_profile_write():
    im_rgb = helpers.gradient_rgb()
    buf = BytesIO()
    # no NCLX profile stored when save_nclx_profile=False
    im_rgb.save(buf, format="HEIF", save_nclx_profile=False)
    assert "nclx_profile" not in Image.open(buf).info
    # sRGB NCLX profile stored by default when save_nclx_profile=True (#365)
    im_rgb.save(buf, format="HEIF", save_nclx_profile=True)
    nclx_out = Image.open(buf).info["nclx_profile"]
    assert nclx_out["color_primaries"] == 1
    assert nclx_out["transfer_characteristics"] == 13
    assert nclx_out["matrix_coefficients"] == 6
    assert nclx_out["full_range_flag"] == 1
    # specify NCLX for the image, color profile should be stored
    nclx_profile = {
        "color_primaries": 4,
        "transfer_characteristics": 4,
        "matrix_coefficients": 0,
        "full_range_flag": 1,
    }
    im_rgb.info["nclx_profile"] = nclx_profile
    im_rgb.save(buf, format="HEIF", save_nclx_profile=True)
    nclx_out = Image.open(buf).info["nclx_profile"]
    for k in nclx_profile:
        assert nclx_profile[k] == nclx_out[k]
    try:
        pillow_heif.options.SAVE_NCLX_PROFILE = False
        im_rgb.save(buf, format="HEIF")
        assert "nclx_profile" not in Image.open(buf).info
        im_rgb.save(buf, format="HEIF", save_nclx_profile=True)
        nclx_out = Image.open(buf).info["nclx_profile"]
        for k in nclx_profile:
            assert nclx_profile[k] == nclx_out[k]
        # here we set the "output" color profile, even if the image has one, it will be overridden.
        nclx_profile = {
            "color_primaries": 1,
            "transfer_characteristics": 1,
            "matrix_coefficients": 10,
            "full_range_flag": 0,
        }
        im_rgb.save(buf, format="HEIF", **nclx_profile, save_nclx_profile=True)
        nclx_out = Image.open(buf).info["nclx_profile"]
        for k in nclx_profile:
            assert nclx_profile[k] == nclx_out[k]
    finally:
        pillow_heif.options.SAVE_NCLX_PROFILE = True


def test_default_nclx_srgb():
    """Test that default save writes sRGB NCLX profile (#365).

    Without explicit NCLX parameters, pillow_heif should write an NCLX
    profile matching libheif's internal sRGB encoding defaults to ensure
    viewers interpret colors correctly.
    """
    srgb_nclx = {
        "color_primaries": 1,  # BT.709
        "transfer_characteristics": 13,  # sRGB (IEC 61966-2-1)
        "matrix_coefficients": 6,  # BT.601-6
        "full_range_flag": 1,
    }
    im_rgb = helpers.gradient_rgb()
    buf = BytesIO()

    # default save (no NCLX params) should produce sRGB NCLX
    im_rgb.save(buf, format="HEIF", quality=90)
    nclx_out = Image.open(buf).info["nclx_profile"]
    for k in srgb_nclx:
        assert srgb_nclx[k] == nclx_out[k]

    # the same but without pillow plugin
    im_heif = pillow_heif.from_pillow(im_rgb)
    buf_heif = BytesIO()
    im_heif.save(buf_heif, quality=90)
    nclx_out = pillow_heif.open_heif(buf_heif).info["nclx_profile"]
    for k in srgb_nclx:
        assert srgb_nclx[k] == nclx_out[k]


def test_default_nclx_srgb_rgba():
    """Test that RGBA images also get sRGB NCLX defaults."""
    im_rgba = helpers.gradient_rgba()
    buf = BytesIO()
    im_rgba.save(buf, format="HEIF", quality=90)
    nclx_out = Image.open(buf).info["nclx_profile"]
    assert nclx_out["color_primaries"] == 1
    assert nclx_out["transfer_characteristics"] == 13
    assert nclx_out["matrix_coefficients"] == 6
    assert nclx_out["full_range_flag"] == 1


def test_explicit_nclx_overrides_defaults():
    """Test that explicit NCLX parameters override sRGB defaults."""
    im_rgb = helpers.gradient_rgb()
    buf = BytesIO()

    # Partial override: only matrix_coefficients
    im_rgb.save(buf, format="HEIF", quality=90, matrix_coefficients=1)
    nclx_out = Image.open(buf).info["nclx_profile"]
    assert nclx_out["matrix_coefficients"] == 1

    # Full override with custom values
    custom_nclx = {
        "color_primaries": 9,
        "transfer_characteristics": 16,
        "matrix_coefficients": 9,
        "full_range_flag": 0,
    }
    im_rgb.save(buf, format="HEIF", quality=90, **custom_nclx)
    nclx_out = Image.open(buf).info["nclx_profile"]
    for k in custom_nclx:
        assert custom_nclx[k] == nclx_out[k]


def test_existing_nclx_profile_preserved():
    """Test that images with existing NCLX profiles are preserved on re-save."""
    hif_path = Path("images/heif_other/cat.hif")
    if not hif_path.exists():
        pytest.skip("Test image not available")
    heif_file = pillow_heif.open_heif(hif_path)
    original_nclx = heif_file.info.get("nclx_profile")
    if original_nclx is None:
        pytest.skip("Test image has no NCLX profile")

    buf = BytesIO()
    heif_file.save(buf, quality=90)
    result_nclx = pillow_heif.open_heif(buf).info["nclx_profile"]
    for k in ("color_primaries", "transfer_characteristics", "matrix_coefficients", "full_range_flag"):
        assert original_nclx[k] == result_nclx[k]


def test_save_nclx_false_no_profile():
    """Test that save_nclx_profile=False suppresses NCLX even with sRGB defaults."""
    im_rgb = helpers.gradient_rgb()
    buf = BytesIO()
    im_rgb.save(buf, format="HEIF", quality=90, save_nclx_profile=False)
    assert "nclx_profile" not in Image.open(buf).info


def test_nclx_disabled_globally_no_default():
    """Test that globally disabled NCLX saving skips sRGB defaults."""
    im_rgb = helpers.gradient_rgb()
    buf = BytesIO()
    try:
        pillow_heif.options.SAVE_NCLX_PROFILE = False
        im_rgb.save(buf, format="HEIF", quality=90)
        assert "nclx_profile" not in Image.open(buf).info
    finally:
        pillow_heif.options.SAVE_NCLX_PROFILE = True


@pytest.mark.parametrize("save_format", ("HEIF",))
def test_lossless_encoding_rgb(save_format):
    im_rgb = helpers.gradient_rgb()
    buf = BytesIO()
    im_rgb.save(buf, format=save_format, quality=-1, chroma=444, matrix_coefficients=0)
    helpers.assert_image_equal(im_rgb, Image.open(buf))


@pytest.mark.parametrize("save_format", ("HEIF",))
def test_lossless_encoding_rgba(save_format):
    im_rgb = helpers.gradient_rgba()
    buf = BytesIO()
    im_rgb.save(buf, format=save_format, quality=-1, chroma=444, matrix_coefficients=0)
    helpers.assert_image_equal(im_rgb, Image.open(buf))


@pytest.mark.parametrize("save_format", ("HEIF",))
def test_lossless_encoding_non_primary_image(save_format):
    def encode_to_image(data):
        binary_data = zlib.compress(data)
        side_length = math.ceil(math.sqrt((len(binary_data) + 3) // 4))
        total_pixels = side_length * side_length
        padded_binary_data = binary_data + b"\x00" * (total_pixels * 4 - len(binary_data))
        binary_array = [tuple(padded_binary_data[i : i + 4]) for i in range(0, len(padded_binary_data), 4)]
        image_data = [binary_array[i : i + side_length] for i in range(0, len(binary_array), side_length)]
        im = Image.new("RGBA", (side_length, side_length))
        im.putdata([pixel for row in image_data for pixel in row])
        return im

    im_rgb = helpers.gradient_rgb()
    im_rgb.encoderinfo = {"matrix_coefficients": 0}
    binary_data_to_encode = b"Some binary data to encode"
    second_image = encode_to_image(binary_data_to_encode)
    second_image.encoderinfo = {"matrix_coefficients": 0}
    buf = BytesIO()
    im_rgb.save(
        buf,
        format=save_format,
        quality=-1,
        chroma=444,
        matrix_coefficients=0,
        save_all=True,
        append_images=[second_image],
    )
    im_out = Image.open(buf)
    helpers.assert_image_equal(im_rgb, im_out)
    bin_data = ImageSequence.Iterator(im_out)[1].copy()
    flattened_binary_array = list(bin_data.getdata())
    binary_data_with_padding = b"".join(bytes(pixel) for pixel in flattened_binary_array)
    z = binary_data_with_padding.rstrip(b"\x00")
    assert zlib.decompress(z) == binary_data_to_encode


def test_input_chroma_value():
    im = Image.open(Path("images/heif_other/RGB_8_chroma444.heif"))
    assert im.info["chroma"] == 444
    im = pillow_heif.open_heif(Path("images/heif_other/RGB_8_chroma444.heif"))
    assert im.info["chroma"] == 444
    im = Image.open(Path("images/heif_other/pug.heic"))
    assert im.info["chroma"] == 420
    im = pillow_heif.open_heif(Path("images/heif_other/pug.heic"))
    assert im.info["chroma"] == 420


@pytest.mark.parametrize("save_format", ("HEIF",))
def test_transparency_parameter(save_format):
    im = Image.new("P", size=(64, 64))
    draw = ImageDraw.Draw(im)
    draw.rectangle(xy=[(0, 0), (32, 32)], fill=255)
    draw.rectangle(xy=[(32, 32), (64, 64)], fill=255)

    buf_png = BytesIO()
    im.save(buf_png, format="PNG", transparency=0)
    im_png = Image.open(buf_png)
    buf_out = BytesIO()
    im_png.save(buf_out, format=save_format, quality=-1)

    helpers.assert_image_equal(im_png.convert("RGBA"), Image.open(buf_out))


def test_invalid_encoder():
    im_rgb = helpers.gradient_rgba()
    buf = BytesIO()
    try:
        pillow_heif.options.PREFERRED_ENCODER["HEIF"] = "invalid_id"
        im_rgb.save(buf, format="HEIF")
    finally:
        pillow_heif.options.PREFERRED_ENCODER["HEIF"] = ""


def _get_tiling_info(buf):
    buf.seek(0)
    return pillow_heif.open_heif(buf).info.get("tiling")


def test_grid_encoding_basic():
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64)

    tiling = _get_tiling_info(buf)
    assert tiling is not None
    assert tiling["num_columns"] == 4
    assert tiling["num_rows"] == 4
    assert tiling["tile_width"] == 64
    assert tiling["tile_height"] == 64
    assert tiling["image_width"] == 256
    assert tiling["image_height"] == 256

    buf.seek(0)
    im_out = Image.open(buf)
    assert im_out.size == (256, 256)
    assert im_out.mode == "RGB"
    helpers.compare_hashes([im, im_out], hash_size=16)


def test_grid_encoding_non_divisible():
    im = helpers.gradient_rgb().resize((301, 201))  # bright colored edges, to detect wrong edge tiles padding
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=128)

    tiling = _get_tiling_info(buf)
    assert tiling is not None
    assert tiling["num_columns"] == 3
    assert tiling["num_rows"] == 2
    assert tiling["tile_width"] == 128
    assert tiling["tile_height"] == 128
    assert tiling["image_width"] == 301
    assert tiling["image_height"] == 201

    buf.seek(0)
    im_out = Image.open(buf)
    assert im_out.size == (301, 201)
    helpers.assert_image_similar(im, im_out, 3.0)

    buf_single = BytesIO()
    im.save(buf_single, format="HEIF")
    im_single = Image.open(buf_single)
    # the right and bottom edge tiles are partial, compare their edges with the single image encoding
    right_columns = (im.size[0] - 2, 0, im.size[0], im.size[1])
    helpers.assert_image_similar(im_single.crop(right_columns), im_out.crop(right_columns), 3.0)
    bottom_rows = (0, im.size[1] - 2, im.size[0], im.size[1])
    helpers.assert_image_similar(im_single.crop(bottom_rows), im_out.crop(bottom_rows), 3.0)


def test_grid_encoding_rgba():
    # images with alpha fall back to single-image encoding: Apple's ImageIO ignores per-tile alpha
    im = helpers.gradient_rgba()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=128)

    assert _get_tiling_info(buf) is None

    buf.seek(0)
    im_out = Image.open(buf)
    assert im_out.size == (256, 256)
    assert im_out.mode == "RGBA"
    helpers.compare_hashes([im, im_out], hash_size=16)
    helpers.assert_image_similar(im.getchannel("A").convert("L"), im_out.getchannel("A").convert("L"), 0.05)


def test_grid_encoding_grayscale():
    im = Image.linear_gradient("L")
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64)

    tiling = _get_tiling_info(buf)
    assert tiling is not None
    assert tiling["num_columns"] == 4
    assert tiling["num_rows"] == 4

    buf.seek(0)
    im_out = Image.open(buf)
    assert im_out.size == (256, 256)
    assert im_out.mode == "L"
    helpers.compare_hashes([im, im_out], hash_size=16)


def test_grid_encoding_la():
    im = helpers.gradient_la()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=128)

    assert _get_tiling_info(buf) is None

    buf.seek(0)
    im_out = Image.open(buf)
    assert im_out.size == (256, 256)
    helpers.compare_hashes([im.convert("RGBA"), im_out], hash_size=16)
    helpers.assert_image_similar(im.getchannel("A").convert("L"), im_out.getchannel("A").convert("L"), 0.05)


def test_grid_encoding_small_image_bypass():
    im = Image.new("RGB", (50, 50), color=(255, 0, 0))
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=128)

    assert _get_tiling_info(buf) is None

    buf.seek(0)
    im_out = Image.open(buf)
    assert im_out.size == (50, 50)


def test_grid_encoding_single_column():
    im = helpers.gradient_rgb().resize((64, 300))  # only the height exceeds the tile size
    buf = BytesIO()
    im.save(buf, format="HEIF", quality=-1, chroma=444, tile_size=128)

    tiling = _get_tiling_info(buf)
    assert (tiling["num_columns"], tiling["num_rows"]) == (1, 3)
    buf.seek(0)
    helpers.assert_image_similar(im, Image.open(buf), 2.0)


def test_grid_encoding_global_option():
    try:
        pillow_heif.options.GRID_TILE_SIZE = 64
        im = helpers.gradient_rgb()
        buf = BytesIO()
        im.save(buf, format="HEIF")

        tiling = _get_tiling_info(buf)
        assert tiling is not None
        assert tiling["num_columns"] == 4
        assert tiling["num_rows"] == 4
    finally:
        pillow_heif.options.GRID_TILE_SIZE = 0


def test_grid_encoding_preserves_exif():
    from PIL.ExifTags import Base as ExifBase

    im = helpers.gradient_rgb()
    exif = Image.Exif()
    exif[ExifBase.Make] = "TestCamera"
    exif[ExifBase.Model] = "TestModel"
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64, exif=exif.tobytes())

    assert _get_tiling_info(buf) is not None

    buf.seek(0)
    im_out = Image.open(buf)
    exif_out = im_out.getexif()
    assert exif_out.get(ExifBase.Make) == "TestCamera"
    assert exif_out.get(ExifBase.Model) == "TestModel"


def test_grid_encoding_preserves_xmp():
    im = helpers.gradient_rgb()
    xmp_data = b'<?xpacket begin="\xef\xbb\xbf"?><x:xmpmeta xmlns:x="adobe:ns:meta/"></x:xmpmeta><?xpacket end="w"?>'
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64, xmp=xmp_data)

    assert _get_tiling_info(buf) is not None

    buf.seek(0)
    im_out = Image.open(buf)
    assert im_out.info.get("xmp") is not None
    assert b"xmpmeta" in im_out.info["xmp"]


def test_grid_encoding_preserves_icc():
    from PIL import ImageCms

    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64, icc_profile=icc)

    assert _get_tiling_info(buf) is not None
    buf.seek(0)
    assert pillow_heif.open_heif(buf).info["icc_profile"] == icc


def test_grid_encoding_standalone_api():
    im = Image.new("RGB", (256, 256), color=(100, 200, 50))
    heif_im = pillow_heif.from_pillow(im)
    buf = BytesIO()
    heif_im.save(buf, tile_size=64)

    tiling = _get_tiling_info(buf)
    assert tiling is not None
    assert tiling["num_columns"] == 4
    assert tiling["num_rows"] == 4

    buf.seek(0)
    heif_out = pillow_heif.open_heif(buf)
    assert heif_out.size == (256, 256)


def test_grid_encoding_multi_image():
    im1 = Image.new("RGB", (256, 256), color=(255, 0, 0))
    im2 = Image.new("RGB", (128, 128), color=(0, 255, 0))
    buf = BytesIO()
    im1.save(buf, format="HEIF", save_all=True, append_images=[im2], tile_size=64)

    buf.seek(0)
    im_out = Image.open(buf)
    assert im_out.n_frames == 2
    assert im_out.size == (256, 256)
    assert im_out.info["tiling"]["num_columns"] == 4
    im_out.seek(1)
    im_out.load()
    assert im_out.size == (128, 128)
    assert im_out.info["tiling"]["num_columns"] == 2

    buf = BytesIO()
    im1.save(buf, format="HEIF", save_all=True, append_images=[im2], tile_size=64, primary_index=1)
    buf.seek(0)
    assert pillow_heif.open_heif(buf).primary_index == 1


def test_grid_encoding_vs_single_roundtrip():
    im = helpers.gradient_rgb()

    buf_single = BytesIO()
    im.save(buf_single, format="HEIF", quality=90)
    buf_single.seek(0)

    buf_grid = BytesIO()
    im.save(buf_grid, format="HEIF", quality=90, tile_size=64)
    buf_grid.seek(0)

    im_single = Image.open(buf_single)
    im_grid = Image.open(buf_grid)

    assert im_single.size == im_grid.size
    assert im_single.mode == im_grid.mode
    helpers.compare_hashes([im_single, im_grid], hash_size=16)


def test_grid_no_tiling_info_for_single_image():
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF")

    assert _get_tiling_info(buf) is None


def test_grid_encoding_nclx_profile():
    srgb_nclx = {
        "color_primaries": 1,
        "transfer_characteristics": 13,
        "matrix_coefficients": 6,
        "full_range_flag": 1,
    }
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", quality=90, tile_size=64)
    assert _get_tiling_info(buf) is not None
    nclx_grid = Image.open(buf).info.get("nclx_profile")
    assert nclx_grid is not None
    for k in srgb_nclx:
        assert srgb_nclx[k] == nclx_grid[k]


def test_grid_encoding_nclx_disabled():
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64, save_nclx_profile=False)
    assert _get_tiling_info(buf) is not None
    assert "nclx_profile" not in Image.open(buf).info


def test_grid_encoding_pixel_aspect_ratio():
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64, pixel_aspect_ratio=(4, 3))

    assert _get_tiling_info(buf) is not None

    buf.seek(0)
    heif_out = pillow_heif.open_heif(buf)
    assert heif_out.info.get("pixel_aspect_ratio") == (4, 3)


def test_grid_encoding_orientation():
    im = Image.effect_mandelbrot((256, 128), (-3, -2.5, 2, 2.5), 100).crop((0, 0, 256, 96))
    im = im.convert(mode="RGB")
    exif_data = Image.Exif()
    exif_data[0x0112] = 6  # 90 CW rotation

    buf_single = BytesIO()
    im.save(buf_single, format="HEIF", quality=-1, exif=exif_data.tobytes())
    im_single = Image.open(buf_single)

    buf_grid = BytesIO()
    im.save(buf_grid, format="HEIF", quality=-1, tile_size=64, exif=exif_data.tobytes())
    im_grid = Image.open(buf_grid)

    assert im_grid.info.get("original_orientation") == 6
    helpers.assert_image_similar(im_single, im_grid)


@pytest.mark.parametrize(
    "im_path,expected_bit_depth,expected_grid",
    (
        ("images/heif/RGB_10__128x128.heif", 10, True),
        ("images/heif/RGB_12__128x128.heif", 12, True),
        ("images/heif/RGBA_12__128x128.heif", 12, False),
    ),
)
def test_grid_encoding_hdr(im_path, expected_bit_depth, expected_grid):
    heif_file = pillow_heif.open_heif(im_path, convert_hdr_to_8bit=False)
    buf = BytesIO()
    heif_file.save(buf, quality=-1, chroma=444, tile_size=64)
    buf_single = BytesIO()
    heif_file.save(buf_single, quality=-1, chroma=444, tile_size=0)

    heif_file_out = pillow_heif.open_heif(buf, convert_hdr_to_8bit=False)
    if expected_grid:
        assert heif_file_out.info["tiling"]["num_columns"] == 2
    else:  # images with alpha fall back to single-image encoding
        assert "tiling" not in heif_file_out.info
    assert heif_file_out.info["bit_depth"] == expected_bit_depth
    helpers.compare_hashes([buf, buf_single], hash_size=16)


@pytest.mark.parametrize("save_to_12bit,expected_bit_depth", ((False, 10), (True, 12)))
def test_grid_encoding_16bit_input(save_to_12bit, expected_bit_depth):
    im = Image.effect_mandelbrot((128, 128), (-3, -2.5, 2, 2.5), 100).convert(mode="I;16")
    heif_file = pillow_heif.from_pillow(im)
    try:
        pillow_heif.options.SAVE_HDR_TO_12_BIT = save_to_12bit
        buf = BytesIO()
        heif_file.save(buf, quality=-1, chroma=444, tile_size=64)
        buf_single = BytesIO()
        heif_file.save(buf_single, quality=-1, chroma=444, tile_size=0)
    finally:
        pillow_heif.options.SAVE_HDR_TO_12_BIT = False

    heif_file_out = pillow_heif.open_heif(buf, convert_hdr_to_8bit=False)
    assert heif_file_out.info["tiling"]["num_columns"] == 2
    assert heif_file_out.info["bit_depth"] == expected_bit_depth
    helpers.compare_hashes([buf, buf_single], hash_size=16)


def test_grid_encoding_stride():
    im = Image.effect_mandelbrot((512, 256), (-3, -2.5, 2, 2.5), 100).convert(mode="RGB")
    buf = BytesIO()
    pillow_heif.encode(im.mode, (257, im.size[1]), im.tobytes(), buf, quality=-1, stride=512 * 3, tile_size=128)
    assert _get_tiling_info(buf) is not None
    im = im.crop((0, 0, 257, 256))
    helpers.compare_hashes([buf, im], hash_size=32)


def test_grid_encoding_nclx_resave():
    nclx_profile = {
        "color_primaries": 9,
        "transfer_characteristics": 16,
        "matrix_coefficients": 9,
        "full_range_flag": 0,
    }
    im = helpers.gradient_rgb()
    im.info["nclx_profile"] = nclx_profile
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64)  # the existing profile values should be written to the grid

    nclx_out = Image.open(buf).info["nclx_profile"]
    for key, value in nclx_profile.items():
        assert nclx_out[key] == value


def test_grid_encoding_nclx_explicit():
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64, matrix_coefficients=0, full_range_flag=1)

    nclx_out = Image.open(buf).info["nclx_profile"]
    assert nclx_out["matrix_coefficients"] == 0
    assert nclx_out["full_range_flag"] == 1


def test_grid_encoding_resave():
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64)

    buf_resave = BytesIO()
    Image.open(buf).save(buf_resave, format="HEIF")  # the grid structure is preserved by default
    tiling = _get_tiling_info(buf_resave)
    assert tiling is not None
    assert tiling["tile_width"] == 64

    buf_resave = BytesIO()
    Image.open(buf).save(buf_resave, format="HEIF", tile_size=128)  # explicit `tile_size` has higher priority
    tiling = _get_tiling_info(buf_resave)
    assert tiling is not None
    assert tiling["tile_width"] == 128

    buf_resave = BytesIO()
    Image.open(buf).save(buf_resave, format="HEIF", tile_size=0)  # zero disables the grid
    assert _get_tiling_info(buf_resave) is None

    try:
        pillow_heif.options.GRID_TILE_SIZE = 512
        buf_resave = BytesIO()
        Image.open(buf).save(buf_resave, format="HEIF")  # the source tile size has priority over the global option
        assert _get_tiling_info(buf_resave)["tile_width"] == 64
    finally:
        pillow_heif.options.GRID_TILE_SIZE = 0


def test_grid_encoding_multi_image_standalone():
    heif_file = pillow_heif.HeifFile()
    heif_file.add_from_pillow(helpers.gradient_rgb())
    heif_file.add_from_pillow(helpers.gradient_rgba().convert("RGB"))
    buf = BytesIO()
    heif_file.save(buf, tile_size=64)

    heif_out = pillow_heif.open_heif(buf)
    assert len(heif_out) == 2
    for im in heif_out:
        assert im.info["tiling"]["tile_width"] == 64


def test_grid_encoding_thumbnails():
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64, thumbnails=[128])

    assert _get_tiling_info(buf) is not None
    buf.seek(0)
    heif_file = pillow_heif.open_heif(buf)
    assert heif_file.info["thumbnails"] == [128]
    im_out = Image.open(buf)
    helpers.compare_hashes([im, im_out], hash_size=16)


def test_grid_encoding_too_many_tiles():
    im = Image.new("RGB", (257 * 64, 64))
    with pytest.raises(ValueError, match="more than 256 rows or columns"):
        im.save(BytesIO(), format="HEIF", tile_size=64)
    im = Image.new("RGB", (40 * 64, 25 * 64))  # 1000 tiles + grid item, default libheif reader limit is 1000 items
    with pytest.raises(ValueError, match="more than 1000 items"):
        im.save(BytesIO(), format="HEIF", tile_size=64)
    im = Image.new("RGB", (25 * 64, 20 * 64))  # 500 tiles per frame, the items limit is for the whole file
    with pytest.raises(ValueError, match="more than 1000 items"):
        im.save(BytesIO(), format="HEIF", save_all=True, append_images=[im], tile_size=64)


def test_grid_encoding_items_limit_boundary():
    im = helpers.gradient_rgb().resize((128, 128))
    heif_file = pillow_heif.from_pillow(im)
    # 4 tiles + grid item + 995 metadata blocks = 1000 items, the file is readable
    heif_file[0].info["metadata"] = [{"type": "cust", "content_type": "", "data": b"1"}] * 995
    buf = BytesIO()
    heif_file.save(buf, tile_size=64)
    out = pillow_heif.open_heif(buf)
    assert out.info["tiling"]["num_columns"] == 2
    assert len(out.info["metadata"]) == 995
    # 1001 items would not be readable, `save` should raise an error before writing anything
    heif_file[0].info["metadata"] = [{"type": "cust", "content_type": "", "data": b"1"}] * 996
    buf = BytesIO()
    with pytest.raises(ValueError, match="more than 1000 items"):
        heif_file.save(buf, tile_size=64)
    assert buf.getbuffer().nbytes == 0


def test_grid_encoding_not_enough_data():
    im = helpers.gradient_rgb().resize((301, 201))
    data = im.tobytes()
    with pytest.raises(ValueError):
        pillow_heif.encode(im.mode, im.size, data[:-5000], BytesIO(), tile_size=128)


def test_grid_encoding_from_pillow_resave():
    im = helpers.gradient_rgb()
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=64)

    buf_resave = BytesIO()
    pillow_heif.from_pillow(Image.open(buf)).save(buf_resave)
    tiling = _get_tiling_info(buf_resave)
    assert tiling is not None
    assert tiling["tile_width"] == 64


def test_grid_encoding_premultiplied_alpha():
    heif_file = pillow_heif.from_pillow(helpers.gradient_rgba())
    heif_file.premultiplied_alpha = True
    buf = BytesIO()
    heif_file.save(buf, quality=-1, tile_size=64)
    out_heif_file = pillow_heif.open_heif(buf)
    assert out_heif_file.info.get("tiling") is None
    assert out_heif_file.premultiplied_alpha


def test_grid_encoding_ycbcr():
    im = Image.new("YCbCr", (256, 128), color=(128, 128, 128))
    with pytest.raises(ValueError):
        im.save(BytesIO(), format="HEIF", tile_size=64)
    with pytest.raises(ValueError):  # the standalone API path raises too
        pillow_heif.encode("YCbCr", (256, 128), bytes(256 * 128 * 3), BytesIO(), tile_size=64)
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=512)
    assert _get_tiling_info(buf) is None
    buf = BytesIO()
    im.save(buf, format="HEIF", tile_size=None)
    assert _get_tiling_info(buf) is None

    buf_rgb = BytesIO()
    helpers.gradient_rgb().save(buf_rgb, format="HEIF", tile_size=64)
    im = Image.open(buf_rgb).convert("YCbCr")  # the source info["tiling"] must be ignored for `YCbCr`
    buf = BytesIO()
    im.save(buf, format="HEIF")
    assert _get_tiling_info(buf) is None


@pytest.mark.skipif(not pillow_heif.libheif_info()["AVIF"], reason="Requires AVIF encoder.")
@pytest.mark.parametrize(
    "mode,size,params,expected_grid",
    (
        ("RGB", (256, 256), {}, True),
        ("RGB", (301, 201), {}, False),  # odd dimensions with subsampled chroma violate MIAF parity rules
        ("RGB", (301, 201), {"chroma": 444}, True),
        ("RGB", (256, 256), {"tile_size": 32}, False),  # MIAF requires tile sizes of at least 64
        ("L", (301, 201), {}, True),  # monochrome images have no chroma parity constraints
    ),
)
def test_grid_encoding_avif(mode, size, params, expected_grid):
    from PIL import AvifImagePlugin, features

    im = helpers.gradient_rgb().resize(size)
    if mode == "L":
        im = im.convert("L")
    buf = BytesIO()
    pillow_heif.from_pillow(im).save(buf, format="AVIF", quality=90, **{"tile_size": 128, **params})
    assert (_get_tiling_info(buf) is not None) == expected_grid
    avif_version = features.version("avif") if features.check("avif") else None
    # libavif-based readers (Pillow, Chrome) must accept every produced file;
    # libavif < 1.1 cannot parse the `iloc` layout libheif writes for multi-item files at all
    if avif_version and tuple(map(int, avif_version.split(".")[:2])) >= (1, 1):
        buf.seek(0)
        im_out = AvifImagePlugin.AvifImageFile(buf)
        im_out.load()
        assert im_out.size == size
        helpers.assert_image_similar(im.convert("RGB"), im_out.convert("RGB"), 5.0)
