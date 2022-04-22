import os
from io import SEEK_END, BytesIO
from pathlib import Path

import dataset
import pytest
from PIL import Image, UnidentifiedImageError

from pillow_heif import open_heif, options, register_heif_opener

register_heif_opener()
os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(not options().avif, reason="missing AV1 codecs.")
def test_avif_cfg_option():
    # when `options.avif` is False, pillow_heif must refuse to open `avif` files
    try:
        options().avif = False
        for file in dataset.AVIF_IMAGES[:3]:
            with pytest.raises(UnidentifiedImageError):
                Image.open(file)
    finally:
        options().reset()


def test_strict_cfg_option():
    # libheif don't fully support burst images, so with strict=True pillow_heif must refuse to open it
    image_path = Path("images/etc_heif/nokia/bird_burst.heic")
    try:
        options().update(strict=True)
        with pytest.raises(UnidentifiedImageError):
            Image.open(image_path)
        options().update(strict=False)
        Image.open(image_path)
    finally:
        options().reset()


def test_thumbnails_option():
    image_path = Path("images/rgb8_128_128_2_1.heic")
    try:
        heif_file = open_heif(image_path)
        assert heif_file.thumbnails
        assert str(heif_file.thumbnails[0]).find("bytes image data") == -1
        assert heif_file.thumbnails[0].data
        assert str(heif_file.thumbnails[0]).find("bytes image data") != -1
        # disabling thumbnails and checking them not to be present
        options().thumbnails = False
        heif_file = open_heif(image_path)
        assert not heif_file.thumbnails
    finally:
        options().reset()


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_quality_option():
    try:
        image = open_heif(Path("images/rgb8_128_128_2_1.heic"))
        options().quality = 10
        out_buf_1_q10 = BytesIO()
        image.save(out_buf_1_q10)
        options().quality = 30
        # passing manual `quality` has higher priority then one in `options`
        out_buf_2_q10 = BytesIO()
        image.save(out_buf_2_q10, quality=10)
        assert out_buf_1_q10.seek(0, SEEK_END) == out_buf_2_q10.seek(0, SEEK_END)
        # image with quality 30% must have bigger size then 10%
        out_buf_3_q30 = BytesIO()
        image.save(out_buf_3_q30)
        assert out_buf_1_q10.seek(0, SEEK_END) < out_buf_3_q30.seek(0, SEEK_END)
    finally:
        options().reset()
