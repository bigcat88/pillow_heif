import builtins
import os
from gc import collect
from io import BytesIO
from pathlib import Path
from typing import Union
from warnings import warn

import pytest
from heif_test import compare_heif_files_fields
from PIL import Image, ImageCms, ImageSequence, UnidentifiedImageError

from pillow_heif import (
    HeifBrand,
    HeifFile,
    HeifImage,
    HeifThumbnail,
    open_heif,
    options,
    register_heif_opener,
)

register_heif_opener()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

avif_images = [f for f in list(Path().glob("images/avif/*.avif"))] + [f for f in list(Path().glob("images/*.avif"))]
heic_images = [f for f in list(Path().glob("images/nokia/*.heic"))] + [f for f in list(Path().glob("images/*.heic"))]
heif_images = [f for f in list(Path().glob("images/*.hif"))] + [f for f in list(Path().glob("images/*.heif"))]

if not options().avif:
    warn("Skipping tests for `AV1` format due to lack of codecs.")
    avif_images.clear()

images_dataset = heic_images + avif_images + heif_images


def compare_heif_to_pillow_fields(heif: Union[HeifFile, HeifImage, HeifThumbnail], pillow: Image, ignore=None):
    def compare_images_fields(heif_image: Union[HeifImage, HeifThumbnail], pillow_image: Image):
        assert heif_image.size == pillow_image.size
        assert heif_image.mode == pillow_image.mode
        is_heif_image = isinstance(heif_image, HeifImage)
        assert is_heif_image == bool(len(pillow_image.info))
        for k in ("main", "brand", "exif", "metadata"):
            if heif_image.info.get(k, None):
                if isinstance(heif_image.info[k], (bool, int, float, str)):
                    assert heif_image.info[k] == pillow_image.info[k]
                else:
                    assert len(heif_image.info[k]) == len(pillow_image.info[k])
        for k in ("icc_profile", "icc_profile_type", "nclx_profile"):
            if heif_image.info.get(k, None):
                assert len(heif_image.info[k]) == len(pillow_image.info[k])

    if isinstance(heif, HeifFile):
        for i, image in enumerate(heif):
            pillow.seek(i)
            compare_images_fields(image, pillow)
    else:
        compare_images_fields(heif, pillow)


@pytest.mark.parametrize("image_path", images_dataset)
def test_open_images(image_path):
    pillow_image = Image.open(image_path)
    assert getattr(pillow_image, "fp") is not None
    assert getattr(pillow_image, "heif_file") is not None
    assert not getattr(pillow_image, "_close_exclusive_fp_after_loading")
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
    if images_count > 1:
        assert getattr(pillow_image, "heif_file") is not None
        assert not getattr(pillow_image, "_close_exclusive_fp_after_loading")
    else:
        assert getattr(pillow_image, "heif_file") is None
        assert getattr(pillow_image, "_close_exclusive_fp_after_loading")


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


@pytest.mark.parametrize("image_path", ("images/pug_2_1.heic", "images/pug_2_3.heic"))
def test_to_from_pillow(image_path):
    heif_file = open_heif(image_path)
    pillow_image1 = heif_file[0].to_pillow()
    pillow_image2 = heif_file[1].to_pillow()
    compare_heif_to_pillow_fields(heif_file[0], pillow_image1)
    compare_heif_to_pillow_fields(heif_file[1], pillow_image2)
    heif_from_pillow = HeifFile({})
    heif_from_pillow.add_from_pillow(pillow_image1)
    heif_from_pillow.add_from_pillow(pillow_image2)
    compare_heif_files_fields(heif_file, heif_from_pillow)


@pytest.mark.parametrize(
    "image_path,compare_info",
    (
        ("images/pug_2_1.heic", {0: [0], 1: []}),
        ("images/pug_2_3.heic", {0: [0], 1: [0, 1]}),
        ("images/nokia/alpha.heic", {0: [], 1: [], 2: []}),
    ),
)
def test_to_from_pillow_extra(image_path, compare_info):
    heif_file = open_heif(image_path)
    pil_list = []
    # HeifFile to Pillow Images list
    for img_i, thumb_i_list in compare_info.items():
        pil_list.append(heif_file[img_i].to_pillow(ignore_thumbnails=True))
        for thumb_i in thumb_i_list:
            pil_list.append(heif_file[img_i].thumbnails[thumb_i].to_pillow())
    collect()
    # Pillow Images compare to HeifFile
    i = 0
    for img_i, thumb_i_list in compare_info.items():
        compare_heif_to_pillow_fields(heif_file[img_i], pil_list[i])
        i += 1
        for thumb_i in thumb_i_list:
            compare_heif_to_pillow_fields(heif_file[img_i].thumbnails[thumb_i], pil_list[i])
            i += 1
    collect()
    # From Pillow Images create one HeifFile and compare.
    heif_from_pillow = HeifFile({})
    i = 0
    for img_i, thumb_i_list in compare_info.items():
        heif_from_pillow.add_from_pillow(pil_list[i])
        i += 1
        for _ in thumb_i_list:
            heif_from_pillow[len(heif_from_pillow) - 1].add_thumbnails(max(pil_list[i].size))
            i += 1
    compare_heif_files_fields(heif_file, heif_from_pillow, thumb_max_differ=3)
