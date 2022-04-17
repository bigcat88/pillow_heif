import os
from io import SEEK_END, BytesIO
from pathlib import Path

import pytest
from PIL import Image, ImageSequence

from pillow_heif import from_pillow, options, register_heif_opener

imagehash = pytest.importorskip("hashes_test", reason="NumPy not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_jpeg_heic():
    jpeg_pillow = Image.open(Path("images/jpeg_gif_png/pug.jpeg"))
    heic_pillow = Image.open(Path("images/pug_1_1.heic"))
    # test decoder basic
    imagehash.compare_hashes([jpeg_pillow, heic_pillow])
    # test jpeg->heic and heic->jpeg
    out_heic = BytesIO()
    jpeg_pillow.save(out_heic, format="HEIF")
    out_jpeg = BytesIO()
    heic_pillow.save(out_jpeg, format="JPEG")
    imagehash.compare_hashes([jpeg_pillow, heic_pillow, out_heic, out_jpeg])


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_jpeg_to_heic_orientation():
    # test jpeg orientation
    jpeg_pillow = Image.open(Path("images/jpeg_gif_png/pug_90_flipped.jpeg"))
    out_heic = BytesIO()
    jpeg_pillow.save(out_heic, format="HEIF", quality=80)
    imagehash.compare_hashes([jpeg_pillow, out_heic], hash_type="dhash", max_difference=1)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_quality():
    # test heic orientation
    heic_pillow = Image.open(Path("images/arrow.heic"))
    out_jpeg = BytesIO()
    heic_pillow.save(out_jpeg, format="JPEG")
    imagehash.compare_hashes([heic_pillow, out_jpeg], hash_type="dhash", max_difference=1)
    out_heic_q30 = BytesIO()
    out_heic_q20 = BytesIO()
    heic_pillow.save(out_heic_q30, format="HEIF", quality=30)
    heic_pillow.save(out_heic_q20, format="HEIF", quality=20)
    imagehash.compare_hashes([heic_pillow, out_heic_q30, out_heic_q20], hash_size=8)
    assert out_heic_q30.seek(0, SEEK_END) < Path("images/arrow.heic").stat().st_size
    assert out_heic_q20.seek(0, SEEK_END) < out_heic_q30.seek(0, SEEK_END)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
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


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
@pytest.mark.parametrize("size", ((1, 0), (0, 1), (0, 0)))
def test_zero(size: tuple):
    out_heif = BytesIO()
    im = Image.new("RGB", size)
    with pytest.raises(ValueError):
        im.save(out_heif, format="HEIF")


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_alpha_channel():
    # saving heic to png
    heic_pillow = Image.open(Path("images/nokia/alpha_3_2.heic"))
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


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_palette_with_bytes_transparency():
    png_pillow = Image.open(Path("images/jpeg_gif_png/palette_with_bytes_transparency.png"))
    heif_file = from_pillow(png_pillow)
    out_heic = BytesIO()
    heif_file.save(out_heic, format="HEIF", quality=90, save_all=True)
    heic_pillow = Image.open(out_heic)
    assert heic_pillow.heif_file.has_alpha is True  # noqa
    assert heic_pillow.mode == "RGBA"
