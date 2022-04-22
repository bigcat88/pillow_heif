import os
from io import SEEK_END, BytesIO
from pathlib import Path

import pytest
from opener_test import compare_heif_to_pillow_fields
from PIL import Image, ImageSequence

from pillow_heif import from_pillow, open_heif, options, register_heif_opener

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


imagehash = pytest.importorskip("compare_hashes", reason="NumPy not installed")
if not options().hevc_enc:
    pytest.skip("No HEVC encoder.", allow_module_level=True)


def test_save_one_all():
    im = Image.open(Path("images/rgb8_128_128_2_1.heic"))
    out_heif1 = BytesIO()
    im.save(out_heif1, format="HEIF")
    assert len(open_heif(out_heif1)) == 1
    out_heif2 = BytesIO()
    im.save(out_heif2, format="HEIF", save_all=True)
    assert len(open_heif(out_heif2)) == 2


@pytest.mark.parametrize("size", ((1, 0), (0, 1), (0, 0)))
def test_zero(size: tuple):
    out_heif = BytesIO()
    im = Image.new("RGB", size)
    with pytest.raises(ValueError):
        im.save(out_heif, format="HEIF")


def test_jpeg_to_heic_with_orientation():
    jpeg_pillow = Image.open(Path("images/jpeg_gif_png/pug_90_flipped.jpeg"))
    out_heic = BytesIO()
    jpeg_pillow.save(out_heic, format="HEIF", quality=100)
    heic_pillow = Image.open(out_heic)
    imagehash.compare_hashes([jpeg_pillow, heic_pillow], hash_type="dhash", hash_size=8)
    out_jpeg = BytesIO()
    heic_pillow.save(out_jpeg, format="JPEG")
    imagehash.compare_hashes([jpeg_pillow, out_jpeg], hash_type="dhash", hash_size=8)


def test_heic_orientation_and_quality():
    heic_pillow = Image.open(Path("images/etc_heif/arrow.heic"))
    out_jpeg = BytesIO()
    heic_pillow.save(out_jpeg, format="JPEG")
    imagehash.compare_hashes([heic_pillow, out_jpeg], hash_type="dhash", max_difference=1)
    out_heic_q30 = BytesIO()
    out_heic_q20 = BytesIO()
    heic_pillow.save(out_heic_q30, format="HEIF", quality=30)
    heic_pillow.save(out_heic_q20, format="HEIF", quality=20)
    imagehash.compare_hashes([heic_pillow, out_heic_q30, out_heic_q20], hash_size=8)
    assert out_heic_q30.seek(0, SEEK_END) < Path("images/etc_heif/arrow.heic").stat().st_size
    assert out_heic_q20.seek(0, SEEK_END) < out_heic_q30.seek(0, SEEK_END)


def test_gif():
    # convert first frame of gif
    gif_pillow = Image.open(Path("images/jpeg_gif_png/chi.gif"))
    out_heic = BytesIO()
    gif_pillow.save(out_heic, format="HEIF")
    imagehash.compare_hashes([gif_pillow, out_heic], hash_type="dhash")
    # convert all frames of gif(pillow_heif does not skip identical frames and saves all frames like in source)
    out_all_heic = BytesIO()
    gif_pillow.save(out_all_heic, format="HEIF", save_all=True, quality=80)
    assert out_heic.seek(0, SEEK_END) * 2 < out_all_heic.seek(0, SEEK_END)
    heic_pillow = Image.open(out_all_heic)
    for i, frame in enumerate(ImageSequence.Iterator(gif_pillow)):
        imagehash.compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame], max_difference=1)


def test_alpha_channel():
    # saving heic to png
    heic_pillow = Image.open(Path("images/etc_heif/nokia/alpha_3_2.heic"))
    out_png = BytesIO()
    heic_pillow.save(out_png, format="PNG", save_all=True)
    png_pillow = Image.open(out_png)
    for i, frame in enumerate(ImageSequence.Iterator(png_pillow)):
        imagehash.compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame])
    # saving from png to heic
    out_heic = BytesIO()
    png_pillow.save(out_heic, format="HEIF", quality=90, save_all=True)
    heic_pillow = Image.open(out_heic)
    for i, frame in enumerate(ImageSequence.Iterator(png_pillow)):
        imagehash.compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame])


def test_palette_with_bytes_transparency():
    png_pillow = Image.open(Path("images/jpeg_gif_png/palette_with_bytes_transparency.png"))
    heif_file = from_pillow(png_pillow)
    out_heic = BytesIO()
    heif_file.save(out_heic, format="HEIF", quality=90, save_all=True)
    heic_pillow = Image.open(out_heic)
    assert heic_pillow.heif_file.has_alpha is True  # noqa
    assert heic_pillow.mode == "RGBA"


def test_append_images():
    heic_pillow = Image.open(Path("images/rgb8_512_512_1_0.heic"))
    heic_pillow2 = Image.open(Path("images/rgb8_150_128_2_1.heic"))
    heic_pillow3 = Image.open(Path("images/rgb10_639_480_1_3.heic"))
    out_buf = BytesIO()
    heic_pillow.save(out_buf, format="HEIF", save_all=True, append_images=[heic_pillow2, heic_pillow3])
    heic_pillow = Image.open(out_buf)
    assert getattr(heic_pillow, "n_frames") == 4
    assert len(ImageSequence.Iterator(heic_pillow)[0].info.get("thumbnails", [])) == 0
    assert len(ImageSequence.Iterator(heic_pillow)[1].info.get("thumbnails", [])) == 1
    assert len(ImageSequence.Iterator(heic_pillow)[2].info.get("thumbnails", [])) == 1
    assert len(ImageSequence.Iterator(heic_pillow)[3].info.get("thumbnails", [])) == 3
    heif_file = from_pillow(heic_pillow)
    assert len(heif_file) == 4
    heic_pillow.seek(0)
    compare_heif_to_pillow_fields(heif_file[0], heic_pillow)
    heic_pillow.seek(1)
    compare_heif_to_pillow_fields(heif_file[1], heic_pillow)
    heic_pillow.seek(2)
    compare_heif_to_pillow_fields(heif_file[2], heic_pillow)
    heic_pillow.seek(3)
    compare_heif_to_pillow_fields(heif_file[3], heic_pillow)
