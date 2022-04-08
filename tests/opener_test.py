import builtins
import os
from gc import collect
from io import BytesIO
from pathlib import Path
from warnings import warn

import pytest
from PIL import Image, ImageCms, ImageSequence, UnidentifiedImageError

from pillow_heif import HeifBrand, options, register_heif_opener

register_heif_opener()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

avif_images = [f for f in list(Path().glob("images/avif/*.avif"))] + [f for f in list(Path().glob("images/*.avif"))]
heic_images = [f for f in list(Path().glob("images/nokia/*.heic"))] + [f for f in list(Path().glob("images/*.heic"))]
heif_images = [f for f in list(Path().glob("images/*.hif"))] + [f for f in list(Path().glob("images/*.heif"))]

if not options().avif:
    warn("Skipping tests for `AV1` format due to lack of codecs.")
    avif_images.clear()

images_dataset = heic_images + avif_images + heif_images


@pytest.mark.parametrize("image_path", images_dataset)
def test_open_images(image_path):
    pillow_image = Image.open(image_path)
    assert getattr(pillow_image, "fp") is not None
    assert getattr(pillow_image, "heif_file") is not None
    pillow_image.verify()  # Here we must check verify, but currently verify do nothing.
    images_count = len([_ for _ in ImageSequence.Iterator(pillow_image)])
    _last_img_id = -1
    for i, image in enumerate(ImageSequence.Iterator(pillow_image)):
        assert image.info
        assert image.info["brand"] != HeifBrand.UNKNOWN.name
        if "icc_profile" in image.info and len(image.info["icc_profile"]) > 0:
            ImageCms.getOpenProfile(BytesIO(pillow_image.info["icc_profile"]))
        assert image.info["img_id"] != _last_img_id
        _last_img_id = image.info["img_id"]
        if not i:
            assert image.info["main"]
        image.load()
    assert getattr(pillow_image, "fp") is not None
    if images_count > 1 or len(pillow_image.info["thumbnails"]):
        assert getattr(pillow_image, "heif_file") is not None
    else:
        assert getattr(pillow_image, "heif_file") is None


@pytest.mark.parametrize("img_path", list(Path().glob("images/invalid/*")))
def test_corrupted_open(img_path):
    with pytest.raises(UnidentifiedImageError):
        Image.open(img_path)
    with pytest.raises(UnidentifiedImageError):
        with open(img_path, "rb") as f:
            Image.open(BytesIO(f.read()))


@pytest.mark.parametrize("img_path", avif_images[:4] + heic_images[4:8])
def test_inputs(img_path):
    with builtins.open(img_path, "rb") as f:
        bytes_io = BytesIO(f.read())
    fh = builtins.open(img_path, "rb")
    for _as in (img_path.as_posix(), bytes_io, fh):
        pillow_image = Image.open(_as)
        assert getattr(pillow_image, "fp") is not None
        pillow_image.load()
        pillow_image.load()


def test_after_load():
    img = Image.open(Path("images/pug_1_0.heic"))
    img.load()
    collect()
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        assert len(frame.tobytes()) > 0
        for thumb in img.info["thumbnails"]:
            assert len(thumb.data) > 0
    img = Image.open(Path("images/pug_1_1.heic"))
    img.load()
    collect()
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        assert len(frame.tobytes()) > 0
        for thumb in img.info["thumbnails"]:
            assert len(thumb.data) > 0
    img = Image.open(Path("images/pug_2_2.heic"))
    img.load()
    collect()
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        assert len(frame.tobytes()) > 0
        for thumb in img.info["thumbnails"]:
            assert len(thumb.data) > 0
