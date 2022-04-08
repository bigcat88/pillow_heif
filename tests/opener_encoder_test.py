import os
from io import SEEK_END, BytesIO
from pathlib import Path

import pytest
from PIL import Image, ImageSequence

from pillow_heif import options, register_heif_opener

imagehash = pytest.importorskip("hashes_test", reason="NumPy not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


def compare_hashes(pillow_images: list, hash_type="average", hash_size=16, max_difference=0):
    image_hashes = []
    for pillow_image in pillow_images:
        if isinstance(pillow_image, (str, Path)):
            pillow_image = Image.open(pillow_image)
        elif isinstance(pillow_image, BytesIO):
            pillow_image = Image.open(pillow_image)
        if hash_type == "dhash":
            image_hash = imagehash.dhash(pillow_image, hash_size)
        elif hash_type == "colorhash":
            image_hash = imagehash.colorhash(pillow_image, hash_size)
        else:
            image_hash = imagehash.average_hash(pillow_image, hash_size)
        for _ in range(len(image_hashes)):
            distance = image_hash - image_hashes[_]
            assert distance <= max_difference
        image_hashes.append(image_hash)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_jpeg_heic():
    jpeg_pillow = Image.open(Path("images/jpeg_gif_png/pug.jpeg"))
    heic_pillow = Image.open(Path("images/pug_1_1.heic"))
    # test decoder basic
    compare_hashes([jpeg_pillow, heic_pillow])
    # test jpeg->heic and heic->jpeg
    out_heic = BytesIO()
    jpeg_pillow.save(out_heic, format="HEIF")
    out_jpeg = BytesIO()
    heic_pillow.save(out_jpeg, format="JPEG")
    compare_hashes([jpeg_pillow, heic_pillow, out_heic, out_jpeg])


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_jpeg_to_heic_orientation():
    # test jpeg orientation
    jpeg_pillow = Image.open(Path("images/jpeg_gif_png/pug_90_flipped.jpeg"))
    out_heic = BytesIO()
    jpeg_pillow.save(out_heic, format="HEIF", quality=80)
    compare_hashes([jpeg_pillow, out_heic], hash_type="dhash", max_difference=1)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_quality():
    # test heic orientation
    heic_pillow = Image.open(Path("images/arrow.heic"))
    out_jpeg = BytesIO()
    heic_pillow.save(out_jpeg, format="JPEG")
    compare_hashes([heic_pillow, out_jpeg], hash_type="dhash", max_difference=1)
    out_heic_q30 = BytesIO()
    out_heic_q20 = BytesIO()
    heic_pillow.save(out_heic_q30, format="HEIF", quality=30)
    heic_pillow.save(out_heic_q20, format="HEIF", quality=20)
    compare_hashes([heic_pillow, out_heic_q30, out_heic_q20], hash_size=8)
    assert out_heic_q30.seek(0, SEEK_END) < Path("images/arrow.heic").stat().st_size
    assert out_heic_q20.seek(0, SEEK_END) < out_heic_q30.seek(0, SEEK_END)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_gif():
    # convert first frame of gif
    gif_pillow = Image.open(Path("images/jpeg_gif_png/chi.gif"))
    out_heic = BytesIO()
    gif_pillow.save(out_heic, format="HEIF")
    compare_hashes([gif_pillow, out_heic], hash_type="dhash")
    # convert all frames of gif(pillow_heif does not skip identical frames and saves all frames like in source)
    out_all_heic = BytesIO()
    gif_pillow.save(out_all_heic, format="HEIF", save_all=True, quality=80)
    assert out_heic.seek(0, SEEK_END) * 2 < out_all_heic.seek(0, SEEK_END)
    heic_pillow = Image.open(out_all_heic)
    for i, frame in enumerate(ImageSequence.Iterator(gif_pillow)):
        compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame], max_difference=1)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_alpha_channel():
    # saving heic to png
    heic_pillow = Image.open(Path("images/nokia/alpha_3_2.heic"))
    out_png = BytesIO()
    heic_pillow.save(out_png, format="PNG", save_all=True)
    png_pillow = Image.open(out_png)
    for i, frame in enumerate(ImageSequence.Iterator(png_pillow)):
        compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame])
    # saving from png to heic
    out_heic = BytesIO()
    png_pillow.save(out_heic, format="HEIF", quality=90, save_all=True)
    heic_pillow = Image.open(out_heic)
    for i, frame in enumerate(ImageSequence.Iterator(png_pillow)):
        compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame])
