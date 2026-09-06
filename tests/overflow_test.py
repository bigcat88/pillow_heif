"""Tests for integer overflow in encode path buffer validation."""

from io import BytesIO

import pytest
from helpers import hevc_enc

import pillow_heif

INT_MAX = 2_147_483_647


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize(
    "mode",
    ("RGB", "RGBA", "LA", "L"),
    ids=("add_plane_rgb", "add_plane_rgba", "add_plane_la", "add_plane_l"),
)
def test_encode_stride_overflow(mode):
    # stride_in=INT_MAX, height=100 -> INT_MAX * 100 overflows int32, bypassing bounds check
    buf = BytesIO()
    with pytest.raises(ValueError, match="does not contain enough data"):
        pillow_heif.encode(mode, (100, 100), b"\x00" * 256, buf, quality=-1, stride=INT_MAX)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize(
    ("mode", "size"),
    (
        ("RGB", (32768, 32768)),  # stride=98304, 98304*32768 > INT_MAX
        ("LA", (32768, 32768)),  # stride=65536, 65536*32768 > INT_MAX
        ("L", (46341, 46341)),  # stride=46341, 46341*46341 > INT_MAX
    ),
    ids=("add_plane_rgb", "add_plane_la", "add_plane_l"),
)
def test_encode_large_dimensions_overflow(mode, size):
    # large dimensions where width * channels * height can overflow int32 with implicit stride
    small_buffer = b"\x00" * (1024 * 1024)
    buf = BytesIO()
    with pytest.raises(ValueError, match="does not contain enough data"):
        pillow_heif.encode(mode, size, small_buffer, buf, quality=-1)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("mode", ("RGB", "RGBA", "LA", "L"))
def test_encode_stride_smaller_than_row(mode):
    # stride_in passes the `stride_in * height` length check but the copy reads
    # `real_stride` (width * bytes_per_pixel) bytes per row -> out-of-bounds read
    buf = BytesIO()
    with pytest.raises(ValueError, match="does not contain enough data"):
        pillow_heif.encode(mode, (1000, 2), b"\x00" * 8, buf, quality=-1, stride=1)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("mode", ("RGB", "RGBA", "LA", "L"))
def test_encode_negative_stride(mode):
    # a negative stride makes `stride_in * height` negative, passing the length check,
    # then `in + stride_in * i` reads before the buffer
    buf = BytesIO()
    with pytest.raises(ValueError, match="does not contain enough data"):
        pillow_heif.encode(mode, (100, 10), b"\x00" * (1024 * 1024), buf, quality=-1, stride=-4000)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("extra", (0, 5))
def test_encode_padded_stride_ok(extra):
    # a stride >= the real row width (extra = padding bytes per row) must still be accepted
    width, height = 64, 32
    stride = width * 3 + extra
    buf = BytesIO()
    pillow_heif.encode("RGB", (width, height), b"\x80" * (stride * height), buf, quality=-1, stride=stride)
    out = pillow_heif.open_heif(buf)[0]
    out.load()
    assert out.size == (width, height)
