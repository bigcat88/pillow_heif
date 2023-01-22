import os
import sys
from io import SEEK_END, BytesIO
from time import perf_counter

import pytest
from helpers import aom_enc, create_heif, hevc_enc
from PIL import Image

from pillow_heif import (
    from_pillow,
    open_heif,
    options,
    register_avif_opener,
    register_heif_opener,
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
@pytest.mark.skipif(not aom_enc(), reason="No AVIF encoder.")
@pytest.mark.parametrize("register_opener", (register_avif_opener, register_heif_opener))
def test_options_change_from_plugin_registering(register_opener):
    try:
        register_opener(thumbnails=False, quality=69, save_to_12bit=True, decode_threads=3)
        assert not options.THUMBNAILS
        assert options.QUALITY == 69
        assert options.SAVE_HDR_TO_12_BIT
        assert options.DECODE_THREADS == 3
    finally:
        options.THUMBNAILS = True
        options.QUALITY = None
        options.SAVE_HDR_TO_12_BIT = False
        options.DECODE_THREADS = 4


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
        options.THUMBNAILS = False
        heif_file = open_heif(heif_buf)
        assert not heif_file.thumbnails
    finally:
        options.THUMBNAILS = True


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
@pytest.mark.skipif(not aom_enc(), reason="No AVIF encoder.")
@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
def test_quality_option(save_format):
    try:
        image = from_pillow(Image.linear_gradient(mode="L"))
        options.QUALITY = 10
        out_buf_1_q10 = BytesIO()
        image.save(out_buf_1_q10, format=save_format)
        options.QUALITY = 30
        # passing manual `quality` has higher priority then one in `options`
        out_buf_2_q10 = BytesIO()
        image.save(out_buf_2_q10, quality=10, format=save_format)
        assert out_buf_1_q10.seek(0, SEEK_END) == out_buf_2_q10.seek(0, SEEK_END)
        # image with quality 30% must have bigger size then 10%
        out_buf_3_q30 = BytesIO()
        image.save(out_buf_3_q30, format=save_format)
        assert out_buf_1_q10.seek(0, SEEK_END) < out_buf_3_q30.seek(0, SEEK_END)
    finally:
        options.QUALITY = None


@pytest.mark.skipif(os.cpu_count() < 2, reason="Requires at least a processor with two cores.")
@pytest.mark.skipif(os.getenv("TEST_DECODE_THREADS", "1") == "0", reason="TEST_DECODE_THREADS set to `0`")
@pytest.mark.skipif(sys.maxsize <= 2147483647, reason="Run test only on 64 bit CPU.")
def test_decode_threads():
    test_image = "images/heif_other/arrow.heic"  # not all images can be decoded using more than one thread
    # As we do not know real performance of hardware, measure relative
    try:
        options.DECODE_THREADS = 1
        start_time_one_thread = perf_counter()
        open_heif(test_image, convert_hdr_to_8bit=False).load()
        total_time_one_thread = perf_counter() - start_time_one_thread
        options.DECODE_THREADS = 2
        start_time_multiply_threads = perf_counter()
        open_heif(test_image, convert_hdr_to_8bit=False).load()
        total_time_multiply_threads = perf_counter() - start_time_multiply_threads
        # decoding in multiply threads should be faster at least by 12%
        assert total_time_one_thread > total_time_multiply_threads * 1.12
    finally:
        options.DECODE_THREADS = 4


def test_plugin_register_unknown_option():
    with pytest.warns(UserWarning, match="Unknown option: unknown_option"):
        register_heif_opener(unknown_option=12345)
