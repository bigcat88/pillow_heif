import builtins
import os
from json import load
from pathlib import Path
from warnings import warn

import pytest
from PIL import Image, UnidentifiedImageError

from pillow_heif import open_heif, options, register_heif_opener

register_heif_opener()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with builtins.open("images_info.json", "rb") as _:
    all_images = load(_)

if not options().avif:
    warn("Skipping tests for `AV1` format due to lack of codecs.")
    all_images = [e for e in all_images if not e["name"].endswith(".avif")]

invalid_images = [e for e in all_images if not e["valid"]]
heif_images = [e for e in all_images if e["valid"]]

heic_images = [e for e in heif_images if e["name"].endswith(".heic")]
hif_images = [e for e in heif_images if e["name"].endswith(".hif")]
avif_images = [e for e in heif_images if e["name"].endswith(".avif")]


@pytest.mark.parametrize("img_info_list", [heic_images[:2] + hif_images[:2] + avif_images[:2]])
def test_avif_cfg_option(img_info_list):
    try:
        options().avif = False
        avif_files = skipped_files = 0
        for img_info in img_info_list:
            try:
                if img_info["name"].endswith(".avif"):
                    avif_files += 1
                Image.open(Path(img_info["file"]))
            except UnidentifiedImageError:
                skipped_files += 1
        assert skipped_files == avif_files
    finally:
        options().reset()


@pytest.mark.parametrize("img_info", [e for e in heif_images if not e["strict"]])
def test_strict_cfg_option(img_info):
    try:
        options().update(strict=True)
        with pytest.raises(UnidentifiedImageError):
            Image.open(Path(img_info["file"]))
        options().update(strict=False)
        Image.open(Path(img_info["file"]))
    finally:
        options().reset()


@pytest.mark.parametrize("img_info", hif_images[:1])
def test_thumbnails_option(img_info):
    try:
        heif_file = open_heif(Path(img_info["file"]))
        assert not heif_file.thumbnails
        heif_file.close()
        options().thumbnails = True
        heif_file = open_heif(Path(img_info["file"]))
        assert heif_file.thumbnails
        assert not heif_file.thumbnails[0].data
        heif_file.close()
        options().thumbnails_autoload = True
        heif_file = open_heif(Path(img_info["file"]))
        assert heif_file.thumbnails[0].data
        assert str(heif_file.thumbnails[0]).find("HeifThumbnail") != -1
    finally:
        options().reset()
