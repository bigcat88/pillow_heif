import builtins
import os
from gc import collect
from io import BytesIO
from pathlib import Path
from typing import Union
from unittest import mock

import dataset
import pytest
from heif_test import compare_heif_files_fields
from PIL import Image, ImageCms, ImageSequence, UnidentifiedImageError

import pillow_heif.HeifImagePlugin  # noqa
from pillow_heif import (
    HeifError,
    HeifFile,
    HeifImage,
    HeifThumbnail,
    from_pillow,
    getxmp,
    open_heif,
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def compare_heif_to_pillow_fields(heif: Union[HeifFile, HeifImage, HeifThumbnail], pillow: Image):
    def compare_images_fields(heif_image: Union[HeifImage, HeifThumbnail], pillow_image: Image):
        assert heif_image.size == pillow_image.size
        assert heif_image.mode == pillow_image.mode
        for k in ("exif", "xmp", "metadata"):
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


@pytest.mark.parametrize("img_path", dataset.CORRUPTED_DATASET)
def test_corrupted_open(img_path):
    with pytest.raises(UnidentifiedImageError):
        Image.open(img_path)
    with pytest.raises(UnidentifiedImageError):
        with open(img_path, "rb") as f:
            Image.open(BytesIO(f.read()))


@pytest.mark.parametrize("img_path", dataset.MINIMAL_DATASET)
def test_inputs(img_path):
    with builtins.open(img_path, "rb") as fh:
        bytes_io = BytesIO(fh.read())
        for fp in [bytes_io, fh, img_path, img_path.as_posix()]:
            pillow_image = Image.open(fp)
            assert getattr(pillow_image, "fp") is not None
            pillow_image.load()
            for frame in ImageSequence.Iterator(pillow_image):
                assert len(frame.tobytes()) > 0
            heif_image = from_pillow(pillow_image)
            compare_heif_to_pillow_fields(heif_image, pillow_image)
            assert len(from_pillow(pillow_image, load_one=True)) == 1
            if getattr(pillow_image, "n_frames") > 1:
                assert getattr(pillow_image, "fp") is not None
            else:
                assert getattr(pillow_image, "fp") is None
            if not isinstance(fp, (Path, str)):
                assert not fp.closed


def test_after_load():
    img = Image.open(Path("images/rgb8_512_512_1_0.heic"))
    assert getattr(img, "heif_file") is not None
    for i in range(3):
        img.load()
        collect()
        assert not getattr(img, "is_animated")
        assert getattr(img, "n_frames") == 1
        assert not img.info["thumbnails"]
        assert getattr(img, "heif_file") is None
        assert len(ImageSequence.Iterator(img)[0].tobytes())
    img = Image.open(Path("images/rgb8_128_128_2_1.heic"))
    for i in range(3):
        collect()
        assert getattr(img, "is_animated")
        assert getattr(img, "n_frames") == 2
        assert len(img.info["thumbnails"]) == 1
        assert getattr(img, "heif_file") is not None
        assert len(ImageSequence.Iterator(img)[0].info["thumbnails"]) == 1
        assert len(ImageSequence.Iterator(img)[1].info["thumbnails"]) == 1
        assert len(ImageSequence.Iterator(img)[0].tobytes())
        assert len(ImageSequence.Iterator(img)[1].tobytes())


@pytest.mark.parametrize("image_path", dataset.MINIMAL_DATASET)
def test_to_from_pillow(image_path):
    heif_file = open_heif(image_path)
    images_list = [i.to_pillow() for i in heif_file]
    for i, image in enumerate(heif_file):
        compare_heif_to_pillow_fields(image, images_list[i])
    heif_from_pillow = HeifFile()
    for image in images_list:
        heif_from_pillow.add_from_pillow(image)
    compare_heif_files_fields(heif_file, heif_from_pillow, ignore=["original_bit_depth"])


@pytest.mark.parametrize("image_path", dataset.FULL_DATASET)
def test_open_images(image_path):
    pillow_image = Image.open(image_path)
    assert getattr(pillow_image, "fp") is not None
    assert getattr(pillow_image, "heif_file") is not None
    assert not getattr(pillow_image, "_close_exclusive_fp_after_loading")
    pillow_image.verify()
    # Here we must check verify, but currently verify just loads thumbnails...
    images_count = len([_ for _ in ImageSequence.Iterator(pillow_image)])
    for i, image in enumerate(ImageSequence.Iterator(pillow_image)):
        assert image.info
        assert image.custom_mimetype in ("image/heic", "image/heif", "image/heif-sequence", "image/avif")
        if "icc_profile" in image.info and len(image.info["icc_profile"]) > 0:
            ImageCms.getOpenProfile(BytesIO(pillow_image.info["icc_profile"]))
        collect()
        assert len(ImageSequence.Iterator(pillow_image)[i].tobytes())
        for thumb in ImageSequence.Iterator(pillow_image)[i].info["thumbnails"]:
            assert len(thumb.data)
        assert isinstance(image.getxmp(), dict)
    if images_count > 1:
        assert getattr(pillow_image, "fp") is not None
        assert getattr(pillow_image, "heif_file") is not None
        assert not getattr(pillow_image, "_close_exclusive_fp_after_loading")
    else:
        assert getattr(pillow_image, "fp") is None
        assert getattr(pillow_image, "heif_file") is None
        assert getattr(pillow_image, "_close_exclusive_fp_after_loading")
        # Testing here one more time, just for sure, that missing `heif_file` not affect anything.
        collect()
        assert pillow_image.tobytes()
        assert len(ImageSequence.Iterator(pillow_image)[0].tobytes())


def test_xmp_tags():
    png_xmp = Image.open(Path("images/jpeg_gif_png/xmp_tags_orientation.png"))
    heif_file = from_pillow(png_xmp)
    heif_pillow = heif_file[0].to_pillow()
    assert getxmp(heif_pillow.info["xmp"])
    assert isinstance(heif_pillow.info["xmp"], bytes)
    assert getxmp(heif_file.info["xmp"])
    assert isinstance(heif_file.info["xmp"], bytes)


def test_image_order():
    img = Image.open(Path("images/etc_heif/nokia/alpha.heic"))
    assert not img.info["primary"]
    img.seek(1)
    assert not img.info["primary"]
    img.seek(2)
    assert img.info["primary"]


def test_truncated_fail():
    truncated_heif = Image.open(Path("images/corrupted/truncated.heic"))
    with pytest.raises(HeifError):
        truncated_heif.load()


@mock.patch("PIL.ImageFile.LOAD_TRUNCATED_IMAGES", True)
def test_truncated_ok():
    truncated_heif = Image.open(Path("images/corrupted/truncated.heic"))
    truncated_heif.load()
