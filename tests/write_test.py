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

if not helpers.hevc_enc() or not helpers.aom_enc():
    pytest.skip("No HEVC or AVIF encoder.", allow_module_level=True)

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


def test_scale():
    heif_buf = helpers.create_heif()
    im_heif = pillow_heif.open_heif(heif_buf)
    assert im_heif[0].size == (512, 512)
    im_heif.scale(256, 256)
    assert im_heif[0].size == (256, 256)
    out_buffer = BytesIO()
    im_heif.save(out_buffer, quality=-1)
    helpers.compare_hashes([heif_buf, out_buffer])


@pytest.mark.parametrize(
    "img",
    (
        helpers.gradient_rgba_bytes("HEIF"),
        "images/heif/RGBA_10.heif",
        "images/heif/RGBA_12.heif",
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
    with mock.patch("pillow_heif.heif.have_encoder_for_format") as mock_func:
        mock_func.return_value = False

        im_heif = pillow_heif.from_pillow(Image.new("L", (64, 64)))
        out_buffer = BytesIO()
        with pytest.raises(pillow_heif.HeifError):
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
    im = pillow_heif.from_pillow(Image.new("RGB", size))
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
    empty_heif_file.save(out_buffer, append_images=heif_file)
    helpers.compare_heif_files_fields(heif_file, pillow_heif.open_heif(out_buffer))
    empty_heif_file.save(out_buffer, append_images=heif_file, save_all=False)
    heif_file = pillow_heif.open_heif(out_buffer)
    assert len(heif_file) == 1


def test_hif_file():
    hif_path = Path("images/heif_other/cat.hif")
    heif_file1 = pillow_heif.open_heif(hif_path)
    assert heif_file1.original_bit_depth == 10
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=1)
    heif_file2 = pillow_heif.open_heif(out_buf)
    assert heif_file2.original_bit_depth == 8
    helpers.compare_heif_files_fields(heif_file1, heif_file2, ignore=["t_stride", "original_bit_depth"])
    helpers.compare_hashes([hif_path, out_buf], hash_size=8)


@pytest.mark.parametrize(
    "im_path",
    (
        "images/heif/L_10",
        "images/heif/L_12",
        "images/heif/RGB_10",
        "images/heif/RGB_12",
        "images/heif/RGBA_10",
        "images/heif/RGBA_12",
    ),
)
@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_hdr_save(im_path, save_format):
    im_path = im_path + (".heif" if save_format == "HEIF" else ".avif")
    heif_file = pillow_heif.open_heif(im_path, convert_hdr_to_8bit=False)
    heif_file_to_add = pillow_heif.HeifFile().add_from_heif(heif_file)
    heif_file.add_from_heif(heif_file_to_add)
    heif_file_to_add = None  # noqa
    collect()
    helpers.compare_heif_files_fields(heif_file[0], heif_file[1])
    out_buf = BytesIO()
    heif_file.save(out_buf, quality=-1, format=save_format, chroma=444)
    heif_file_out = pillow_heif.open_heif(out_buf, convert_hdr_to_8bit=False)
    assert len(heif_file_out) == 2
    helpers.compare_heif_files_fields(heif_file[0], heif_file_out[0])
    helpers.compare_heif_files_fields(heif_file[1], heif_file_out[1])
    helpers.compare_heif_files_fields(heif_file_out[0], heif_file_out[1])
    helpers.compare_hashes([im_path, out_buf], hash_size=32)


def test_encoder_parameters():
    out_buf1 = BytesIO()
    out_buf2 = BytesIO()
    heif_buf = helpers.create_heif()
    im_heif = pillow_heif.open_heif(heif_buf)
    im_heif.save(out_buf1, enc_params=[("x265:ctu", "32"), ("x265:min-cu-size", "16"), ("x265:rdLevel", "2")])
    im_heif.save(out_buf2, enc_params=[("x265:ctu", "64"), ("x265:min-cu-size", "8"), ("x265:rdLevel", "6")])
    assert out_buf1.seek(0, SEEK_END) != out_buf2.seek(0, SEEK_END)


def test_pillow_heif_orientation():
    heic_pillow = Image.open(Path("images/heif_other/arrow.heic"))
    out_jpeg = BytesIO()
    heic_pillow.save(out_jpeg, format="JPEG")
    helpers.compare_hashes([heic_pillow, out_jpeg], max_difference=1)


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
    helpers.compare_hashes([im_buffer, im_heif], hash_size=8)


@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_PA_color_mode(save_format):  # noqa
    im_buffer = BytesIO(helpers.gradient_pa_bytes(im_format="TIFF"))
    out_heic = BytesIO()
    im = Image.open(im_buffer)
    im.save(out_heic, format=save_format, quality=90)
    im_heif = Image.open(out_heic)
    assert im_heif.mode == "RGBA"
    helpers.compare_hashes([im_buffer, im_heif], hash_size=8)


@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_L_color_mode(save_format):  # noqa
    im = Image.linear_gradient(mode="L")
    out_heif = BytesIO()
    im.save(out_heif, format=save_format, quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGB"
    helpers.compare_hashes([im, im_heif], hash_size=8)


@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_LA_color_mode(save_format):  # noqa
    im = Image.open(BytesIO(helpers.gradient_la_bytes(im_format="PNG")))
    out_heif = BytesIO()
    im.save(out_heif, format=save_format, quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGBA"
    helpers.compare_hashes([im, im_heif], hash_size=8)


def test_1_color_mode():
    im = Image.linear_gradient(mode="L")
    im = im.convert(mode="1")
    assert im.mode == "1"
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF", quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGB"
    helpers.compare_hashes([im, im_heif], hash_size=8)


def test_CMYK_color_mode():  # noqa
    im = helpers.gradient_rgba().convert("CMYK")
    assert im.mode == "CMYK"
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF", quality=-1)
    im_heif = Image.open(out_heif)
    assert im_heif.mode == "RGBA"
    helpers.compare_hashes([im, im_heif], hash_size=8)


@pytest.mark.parametrize("enc_bits", (10, 12))
@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_I_color_modes_to_10_12_bit(enc_bits, save_format):  # noqa
    try:
        pillow_heif.options().save_to_12bit = True if enc_bits == 12 else False
        src_pillow = Image.open(Path("images/non_heif/L_16.png"))
        assert src_pillow.mode == "I"
        for mode in ("I", "I;16", "I;16L"):
            i_mode_img = src_pillow.convert(mode=mode)
            out_heic = BytesIO()
            i_mode_img.save(out_heic, format=save_format, quality=-1)
            assert pillow_heif.open_heif(out_heic, convert_hdr_to_8bit=False).bit_depth == enc_bits
            heic_pillow = Image.open(out_heic)
            helpers.compare_hashes([src_pillow, heic_pillow], hash_size=8)
    finally:
        pillow_heif.options().reset()


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
        helpers.compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame], max_difference=1)


def test_pillow_append_images():
    im_heif = Image.open(helpers.create_heif((51, 49), thumb_boxes=[16], n_images=2))
    heif_file2 = pillow_heif.open_heif(helpers.create_heif((81, 79), thumb_boxes=[32], n_images=2))
    heif_file3 = pillow_heif.open_heif(helpers.create_heif((72, 68), thumb_boxes=[32, 16], n_images=2))
    out_buf = BytesIO()
    im_heif.save(out_buf, format="HEIF", append_images=[im_heif, heif_file2[1], heif_file3], save_all=True)
    heif_file_out = pillow_heif.open_heif(out_buf)
    assert len([i for i in heif_file_out.thumbnails_all()]) == 2 + 2 + 1 + 4
    assert len(heif_file_out) == 2 + 2 + 1 + 2
    helpers.compare_heif_files_fields(heif_file_out[0], heif_file_out[2])
    helpers.compare_heif_files_fields(heif_file_out[1], heif_file_out[3])
    helpers.compare_heif_files_fields(heif_file2[1], heif_file_out[4])
    helpers.compare_heif_files_fields(heif_file3[0], heif_file_out[5])
    helpers.compare_heif_files_fields(heif_file3[1], heif_file_out[6])


def test_add_from():
    heif_file1_buf = helpers.create_heif()
    heif_file1 = pillow_heif.open_heif(heif_file1_buf)
    heif_file2_buf = helpers.create_heif((210, 128), thumb_boxes=[48, 32], n_images=2)
    heif_file2 = pillow_heif.open_heif(heif_file2_buf)
    heif_file1.add_from_heif(heif_file2, load_one=True)
    heif_file1.add_from_heif(heif_file2[1], load_one=True)
    heif_file1.add_from_heif(heif_file2[1])
    collect()
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=-1)
    out_heif = pillow_heif.open_heif(out_buf)
    assert len(out_heif) == 4
    assert len(list(out_heif.thumbnails_all(one_for_image=True))) == 3
    assert len(list(out_heif.thumbnails_all(one_for_image=False))) == 6
    helpers.compare_heif_files_fields(heif_file1[0], out_heif[0])
    helpers.compare_heif_files_fields(heif_file2[0], out_heif[1])
    helpers.compare_heif_files_fields(heif_file2[1], out_heif[2])
    helpers.compare_heif_files_fields(heif_file2[1], out_heif[3])
    pillow_image = Image.open(out_buf)
    helpers.compare_hashes([pillow_image, heif_file1_buf])
    pillow_image.seek(1)
    pillow_original = Image.open(heif_file2_buf)
    helpers.compare_hashes([pillow_image, pillow_original])
    pillow_image.seek(2)
    pillow_original.seek(1)
    helpers.compare_hashes([pillow_image, pillow_original], max_difference=1)


def test_remove():
    heif_buf = helpers.create_heif((72, 68), thumb_boxes=[32], n_images=2)
    out_buffer = BytesIO()
    # clear list with images
    heif_file = pillow_heif.open_heif(heif_buf)
    heif_file.images.clear()
    assert len(heif_file) == 0
    # removing first image
    heif_file = pillow_heif.open_heif(heif_buf)
    del heif_file[0]
    heif_file.save(out_buffer)
    _ = pillow_heif.open_heif(out_buffer)
    assert len(_) == 1
    assert len(_.thumbnails) == 1
    assert _.size == (36, 34)
    # removing second and first image
    heif_file = pillow_heif.open_heif(heif_buf)
    del heif_file[1]
    del heif_file[0]
    assert len(heif_file) == 0


def test_heif_save_multi_frame():
    heif_file = pillow_heif.open_heif(Path("images/heif_other/nokia/alpha.heic"), convert_hdr_to_8bit=False)
    heif_buf = BytesIO()
    heif_file.save(heif_buf, quality=-1)
    out_heif_file = pillow_heif.open_heif(heif_buf, convert_hdr_to_8bit=False)
    for i in range(3):
        assert heif_file[i].size == out_heif_file[i].size
        assert heif_file[i].mode == out_heif_file[i].mode
        assert heif_file[i].bit_depth == out_heif_file[i].bit_depth
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
