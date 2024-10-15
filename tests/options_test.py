import os
import sys
from io import SEEK_END, BytesIO
from platform import machine
from time import perf_counter
from unittest import mock

import pytest
from helpers import aom, create_heif, hevc_enc
from PIL import Image, UnidentifiedImageError

from pillow_heif import (
    from_pillow,
    open_heif,
    options,
    read_heif,
    register_avif_opener,
    register_heif_opener,
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
@pytest.mark.skipif(not aom(), reason="Requires AVIF support.")
@pytest.mark.parametrize("register_opener", (register_avif_opener, register_heif_opener))
def test_options_change_from_plugin_registering(register_opener):
    try:
        register_opener(
            thumbnails=False,
            quality=69,
            save_to_12bit=True,
            decode_threads=3,
            depth_images=False,
            aux_images=False,
            save_nclx_profile=False,
            preferred_encoder={"HEIF": "id1", "AVIF": "id2"},
            preferred_decoder={"HEIF": "id3", "AVIF": "id4"},
        )
        assert not options.THUMBNAILS
        assert options.QUALITY == 69
        assert options.SAVE_HDR_TO_12_BIT
        assert options.DECODE_THREADS == 3
        assert options.DEPTH_IMAGES is False
        assert options.AUX_IMAGES is False
        assert options.SAVE_NCLX_PROFILE is False
        assert options.PREFERRED_ENCODER == {"HEIF": "id1", "AVIF": "id2"}
        assert options.PREFERRED_DECODER == {"HEIF": "id3", "AVIF": "id4"}
    finally:
        options.THUMBNAILS = True
        options.QUALITY = None
        options.SAVE_HDR_TO_12_BIT = False
        options.DECODE_THREADS = 4
        options.DEPTH_IMAGES = True
        options.AUX_IMAGES = True
        options.SAVE_NCLX_PROFILE = True
        options.PREFERRED_ENCODER = {"HEIF": "", "AVIF": ""}
        options.PREFERRED_DECODER = {"HEIF": "", "AVIF": ""}


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
def test_thumbnails_option():
    heif_buf = create_heif((128, 128), [64])
    try:
        heif_file = open_heif(heif_buf)
        assert heif_file.info["thumbnails"]
        # disabling thumbnails and checking them not to be present
        options.THUMBNAILS = False
        heif_file = open_heif(heif_buf)
        assert not heif_file.info["thumbnails"]
    finally:
        options.THUMBNAILS = True


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
@pytest.mark.skipif(not aom(), reason="Requires AVIF support.")
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
@pytest.mark.skipif(machine() in ("arm64", "aarch64") and sys.platform.lower() == "linux", reason="skip emulator")
def test_decode_threads():
    test_image = "images/heif_other/arrow.heic"  # not all images can be decoded using more than one thread
    # As we do not know real performance of hardware, measure relative
    try:
        options.DECODE_THREADS = 1
        start_time_one_thread = perf_counter()
        read_heif(test_image, convert_hdr_to_8bit=False)
        total_time_one_thread = perf_counter() - start_time_one_thread
        options.DECODE_THREADS = 2
        start_time_multiply_threads = perf_counter()
        read_heif(test_image, convert_hdr_to_8bit=False)
        total_time_multiply_threads = perf_counter() - start_time_multiply_threads
        # decoding in multiply threads should be faster at least by 10%
        assert total_time_one_thread > total_time_multiply_threads * 1.1
    finally:
        options.DECODE_THREADS = 4


def test_allow_incorrect_headers():
    test_image = "images/heif_special/L_8__29(255)x100.heif"
    with pytest.raises(expected_exception=(UnidentifiedImageError, ValueError)):  # noqa
        Image.open(test_image).load()
    register_heif_opener(allow_incorrect_headers=True)
    assert options.ALLOW_INCORRECT_HEADERS
    Image.open(test_image).load()
    register_heif_opener(allow_incorrect_headers=False)
    assert not options.ALLOW_INCORRECT_HEADERS


def test_plugin_register_unknown_option():
    with pytest.warns(UserWarning, match="Unknown option: unknown_option"):
        register_heif_opener(unknown_option=12345)


@mock.patch("pillow_heif.options.DEPTH_IMAGES", False)
def test_depth_option():
    register_heif_opener()
    im = open_heif("images/heif_other/pug.heic")
    assert not im.info["depth_images"]
    im = Image.open("images/heif_other/pug.heic")
    assert not im.info["depth_images"]
