import os
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from pillow_heif import open_heif, register_heif_opener

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


def test_scale():
    heic_file = open_heif(Path("images/pug_1_0.heic"))
    heic_file.scale(640, 640)
    out_buffer = BytesIO()
    heic_file.save(out_buffer)
    compare_hashes([Path("images/pug_1_0.heic"), out_buffer], max_difference=1)
