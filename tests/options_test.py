import os
from io import SEEK_END, BytesIO
from pathlib import Path

import pytest
from PIL import Image, UnidentifiedImageError

from pillow_heif import open_heif, options, register_heif_opener

register_heif_opener()
os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(not options().avif, reason="missing AV1 codecs.")
def test_avif_cfg_option():
    try:
        options().avif = False
        for file in list(Path().glob("images/avif/*.avif")):
            with pytest.raises(UnidentifiedImageError):
                Image.open(file)
    finally:
        options().reset()


def test_strict_cfg_option():
    image_path = Path("images/nokia/bird_burst.heic")
    try:
        options().update(strict=True)
        with pytest.raises(UnidentifiedImageError):
            Image.open(image_path)
        options().update(strict=False)
        Image.open(image_path)
    finally:
        options().reset()


def test_thumbnails_option():
    image_path = Path("images/pug_1_1.heic")
    try:
        heif_file = open_heif(image_path)
        assert heif_file.thumbnails
        assert str(heif_file.thumbnails[0]).find("bytes image data") == -1
        assert heif_file.thumbnails[0].data
        assert str(heif_file.thumbnails[0]).find("bytes image data") != -1
        heif_file.close()
        options().thumbnails = False
        heif_file = open_heif(image_path)
        assert not heif_file.thumbnails
        heif_file.close()
    finally:
        options().reset()


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_quality_option():
    try:
        image = open_heif(Path("images/pug_1_1.heic"))
        options().quality = 10
        out_buf1 = BytesIO()
        image.save(out_buf1)
        options().quality = 30
        out_buf2 = BytesIO()
        image.save(out_buf2)
        assert out_buf1.seek(0, SEEK_END) < out_buf2.seek(0, SEEK_END)
    finally:
        options().reset()
