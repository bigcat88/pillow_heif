import os
from io import SEEK_END, BytesIO
from pathlib import Path

import pytest
from helpers import create_heif, hevc_enc
from PIL import Image, UnidentifiedImageError

from pillow_heif import from_pillow, open_heif, options, register_heif_opener

register_heif_opener()
os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(not options().avif, reason="missing AV1 codecs.")
def test_avif_cfg_option():
    # when `options.avif` is False, pillow_heif must refuse to open `avif` files
    try:
        options().avif = False
        with pytest.raises(UnidentifiedImageError):
            Image.open(Path("images/heif/L_10.avif"))
    finally:
        options().reset()
    Image.open(Path("images/heif/L_10.avif"))


def test_strict_cfg_option():
    # libheif don't fully support burst images, so with strict=True pillow_heif should refuse them
    image_path = Path("images/heif_other/nokia/bird_burst.heic")
    try:
        options().update(strict=True)
        with pytest.raises(UnidentifiedImageError):
            Image.open(image_path)
        options().update(strict=False)
        assert getattr(Image.open(image_path), "n_frames") == 4
    finally:
        options().reset()


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
def test_thumbnails_option():
    heif_buf = create_heif((128, 128), [64])
    try:
        heif_file = open_heif(heif_buf)
        assert heif_file.thumbnails
        assert str(heif_file.thumbnails[0]).find("bytes image data") == -1
        assert heif_file.thumbnails[0].data
        assert str(heif_file.thumbnails[0]).find("bytes image data") != -1
        # disabling thumbnails and checking them not to be present
        options().thumbnails = False
        heif_file = open_heif(heif_buf)
        assert not heif_file.thumbnails
    finally:
        options().reset()


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
def test_quality_option():
    try:
        image = from_pillow(Image.linear_gradient(mode="L"))
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
