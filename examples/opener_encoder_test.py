import os
from pathlib import Path

import imagehash
from PIL import Image, ImageSequence

from pillow_heif import register_heif_opener

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


def compare_hashes(pillow_images: list, hash_type="average", hash_size=16, max_difference=0):
    image_hashes = []
    for pillow_image in pillow_images:
        if isinstance(pillow_image, (str, Path)):
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


def test_jpeg_heic():
    jpeg_pillow = Image.open(Path("images/pug.jpeg"))
    heic_pillow = Image.open(Path("images/pug.heic"))
    # test decoder basic
    compare_hashes([jpeg_pillow, heic_pillow])
    # test jpeg->heic and heic->jpeg
    jpeg_pillow.save(Path("tmp/pug_saved.heic"))
    heic_pillow.save(Path("tmp/pug_saved.jpeg"))
    compare_hashes([jpeg_pillow, heic_pillow, Path("tmp/pug_saved.heic"), Path("tmp/pug_saved.jpeg")])


def test_jpeg_to_heic_orientation():
    # test jpeg orientation
    jpeg_pillow = Image.open(Path("images/pug_90_flipped.jpeg"))
    jpeg_pillow.save(Path("tmp/pug_saved.heic"), quality=80)
    compare_hashes([jpeg_pillow, Path("tmp/pug_saved.heic")], hash_type="dhash", max_difference=1)
    # here later add test with `irot` changing.


def test_quality():
    # test heic orientation
    heic_pillow = Image.open(Path("images/arrow.heic"))
    heic_pillow.save(Path("tmp/arrow.jpeg"))
    compare_hashes([heic_pillow, Path("tmp/arrow.jpeg")], hash_type="dhash", max_difference=1)
    heic_pillow.save(Path("tmp/arrow_q30.heic"), quality=30)
    heic_pillow.save(Path("tmp/arrow_q20.heic"), quality=20)
    compare_hashes([heic_pillow, Path("tmp/arrow_q30.heic"), Path("tmp/arrow_q20.heic")], hash_size=8)
    assert Path("tmp/arrow_q30.heic").stat().st_size < Path("images/arrow.heic").stat().st_size
    assert Path("tmp/arrow_q20.heic").stat().st_size < Path("tmp/arrow_q30.heic").stat().st_size


def test_gif():
    # convert first frame of gif
    gif_pillow = Image.open(Path("images/chi.gif"))
    gif_pillow.save(Path("tmp/chi.heic"))
    compare_hashes([gif_pillow, Path("tmp/chi.heic")], hash_type="dhash")
    # convert all frames of gif(pillow_heif does not skip identical frames and saves all frames like in source)
    gif_pillow.save(Path("tmp/chi_all.heic"), save_all=True, quality=80)
    assert Path("tmp/chi.heic").stat().st_size * 2 < Path("tmp/chi_all.heic").stat().st_size
    heic_pillow = Image.open(Path("tmp/chi_all.heic"))
    for i, frame in enumerate(ImageSequence.Iterator(gif_pillow)):
        compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame], max_difference=1)


def test_alpha_channel():
    # saving heic to png
    heic_pillow = Image.open(Path("images/nokia/alpha/alpha_1440x960.heic"))
    heic_pillow.save(Path("tmp/alpha.png"), save_all=True)
    png_pillow = Image.open(Path("tmp/alpha.png"))
    for i, frame in enumerate(ImageSequence.Iterator(png_pillow)):
        compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame])
    # saving from png to heic
    png_pillow.save(Path("tmp/alpha.heic"), save_all=True)
    heic_pillow = Image.open(Path("tmp/alpha.heic"))
    for i, frame in enumerate(ImageSequence.Iterator(png_pillow)):
        compare_hashes([ImageSequence.Iterator(heic_pillow)[i], frame])
