import os
from io import SEEK_END, BytesIO

import pytest
from helpers import aom_enc, create_heif, hevc_enc
from PIL import Image

from pillow_heif import from_pillow, open_heif, options, register_heif_opener

register_heif_opener()
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def test_options_update():
    try:
        options().update(quality=33, thumbnails=False)
        assert not options().thumbnails
        assert options().quality == 33
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
def test_heif_quality_option():
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


@pytest.mark.skipif(not aom_enc(), reason="No AVIF encoder.")
def test_avif_quality_option():
    try:
        image = from_pillow(Image.linear_gradient(mode="L"))
        options().quality = 10
        out_buf_1_q10 = BytesIO()
        image.save(out_buf_1_q10, format="AVIF")
        options().quality = 30
        # passing manual `quality` has higher priority then one in `options`
        out_buf_2_q10 = BytesIO()
        image.save(out_buf_2_q10, quality=10, format="AVIF")
        assert out_buf_1_q10.seek(0, SEEK_END) == out_buf_2_q10.seek(0, SEEK_END)
        # image with quality 30% must have bigger size then 10%
        out_buf_3_q30 = BytesIO()
        image.save(out_buf_3_q30, format="AVIF")
        assert out_buf_1_q10.seek(0, SEEK_END) < out_buf_3_q30.seek(0, SEEK_END)
    finally:
        options().reset()
