import gc
from io import BytesIO
from pathlib import Path

import helpers
import pytest
from PIL import Image, ImageSequence

try:
    import numpy as np
except ImportError:  # there are no `numpy` wheels for some platforms, like `cp310` on Windows ARM64
    np = None

import pillow_heif

pillow_heif.register_heif_opener()
if not helpers.hevc_enc():
    pytest.skip(reason="Requires HEVC encoder.", allow_module_level=True)

# `libheif` aligns the stride to 16 bytes, so a decoded plane needs compacting for most widths
WIDTHS = (64, 65, 66, 67, 68, 100, 127, 128)


def encoded(mode: str, size: tuple) -> bytes:
    im = helpers.gradient_rgb().resize(size).convert(mode=mode)
    buf = BytesIO()
    pillow_heif.from_pillow(im).save(buf, quality=-1, chroma=444)
    return buf.getvalue()


def borrowed(im: Image.Image) -> bool:
    """The plane is borrowed exactly when Pillow marked the storage read-only."""
    return bool(im.im.readonly)


@pytest.mark.parametrize("mode", ("L", "RGB", "RGBA"))
@pytest.mark.parametrize("width", WIDTHS)
def test_plugin_borrows_the_plane(mode, width):
    data = encoded(mode, (width, 64))
    im = Image.open(BytesIO(data))
    im.load()
    assert borrowed(im)
    # same pixels as decoding without the Pillow layout and copying them the old way
    heif_image = pillow_heif.open_heif(BytesIO(data))[0]
    expected = Image.frombytes(heif_image.mode, heif_image.size, heif_image.data, "raw", heif_image.mode)
    assert im.mode == expected.mode
    helpers.assert_image_equal(im, expected)


@pytest.mark.parametrize("mode", ("L", "RGB", "RGBA"))
def test_to_pillow_borrows_only_with_pillow_layout(mode):
    data = encoded(mode, (128, 64))
    # without the flag `to_pillow` copies as it always did, and the image stays writable
    default = pillow_heif.open_heif(BytesIO(data))[0].to_pillow()
    assert not borrowed(default)
    default.load()[0, 0] = default.getpixel((1, 1))
    assert borrowed(pillow_heif.open_heif(BytesIO(data), pillow_layout=True)[0].to_pillow())


@pytest.mark.skipif(np is None, reason="`numpy` not installed")
@pytest.mark.parametrize("mode", ("L", "RGB", "RGBA"))
def test_numpy_array_does_not_depend_on_the_layout(mode):
    data = encoded(mode, (128, 64))
    expected = np.asarray(pillow_heif.open_heif(BytesIO(data))[0])
    result = np.asarray(pillow_heif.open_heif(BytesIO(data), pillow_layout=True)[0])
    assert result.shape == expected.shape
    assert np.array_equal(result, expected)


@pytest.mark.skipif(np is None, reason="`numpy` not installed")
def test_numpy_array_of_a_padded_pillow_layout_plane():
    data = encoded("RGB", (101, 64))
    heif_image = pillow_heif.open_heif(BytesIO(data), remove_stride=False, pillow_layout=True)[0]
    heif_image.load()
    assert heif_image.stride != heif_image.size[0] * 4
    arr = np.asarray(heif_image)
    # rows are padded, and as always the padding shows up as columns after the image
    assert arr.shape == (64, heif_image.stride // 4, 3)
    assert np.array_equal(arr[:, :101], np.asarray(pillow_heif.open_heif(BytesIO(data))[0]))


@pytest.mark.parametrize("pillow_layout", (False, True))
def test_to_pillow_pixels_do_not_depend_on_the_layout(pillow_layout):
    data = encoded("RGB", (128, 64))
    expected = pillow_heif.open_heif(BytesIO(data))[0].to_pillow()
    result = pillow_heif.open_heif(BytesIO(data), pillow_layout=pillow_layout)[0].to_pillow()
    helpers.assert_image_equal(result, expected)


def test_borrowed_image_is_copy_on_write():
    heif_file = pillow_heif.open_heif(BytesIO(encoded("RGBA", (128, 64))), pillow_layout=True)
    heif_image = heif_file[0]
    im = heif_image.to_pillow()
    assert borrowed(im)
    before = bytes(heif_image.data[:16])
    im.putpixel((0, 0), (1, 2, 3, 4))
    assert im.getpixel((0, 0)) == (1, 2, 3, 4)
    assert not borrowed(im)  # writing detached the image from the plane
    assert bytes(heif_image.data[:16]) == before


def test_borrowed_image_pixel_access_is_read_only():
    # Pillow marks borrowed storage read-only, so writing through the object `load` returns fails.
    # Every other way of changing an image copies it first, see `test_borrowed_image_is_copy_on_write`.
    im = Image.open(BytesIO(encoded("RGB", (128, 64))))
    pixels = im.load()
    assert pixels[0, 0] == im.getpixel((0, 0))
    with pytest.raises(ValueError, match="readonly"):
        pixels[0, 0] = (1, 2, 3)
    im.putpixel((0, 0), (1, 2, 3))  # detaches the image from the plane
    im.load()[1, 1] = (4, 5, 6)
    assert im.getpixel((1, 1)) == (4, 5, 6)


def test_borrowed_images_do_not_share_writes():
    heif_image = pillow_heif.open_heif(BytesIO(encoded("RGBA", (128, 64))), pillow_layout=True)[0]
    first, second = heif_image.to_pillow(), heif_image.to_pillow()
    original = second.getpixel((5, 5))
    first.putpixel((5, 5), (9, 9, 9, 9))
    assert second.getpixel((5, 5)) == original


def test_borrowed_image_outlives_the_heif_file():
    im = Image.open(BytesIO(encoded("RGB", (128, 64))))
    im.load()
    assert borrowed(im)
    expected = im.tobytes()
    del im.info["depth_images"], im.info["aux"]
    gc.collect()
    bytearray(16 * 1024 * 1024)  # churn the allocator over anything that was freed
    gc.collect()
    assert im.tobytes() == expected


def test_arrow_c_array_shares_the_plane():
    heif_image = pillow_heif.open_heif(BytesIO(encoded("RGB", (128, 64))), pillow_layout=True)[0]
    schema_capsule, array_capsule = heif_image.__arrow_c_array__()
    assert "arrow_schema" in repr(schema_capsule)
    assert "arrow_array" in repr(array_capsule)
    assert "arrow_schema" in repr(heif_image.__arrow_c_schema__())
    im = Image.fromarrow(heif_image, "RGB", heif_image.size)
    assert borrowed(im)
    helpers.assert_image_equal(im, heif_image.to_pillow())


@pytest.mark.skipif(np is None, reason="`numpy` not installed")
def test_arrow_shares_a_16bit_plane():
    im16 = helpers.gradient_rgb().resize((128, 64)).convert("L").convert("I;16")
    buf = BytesIO()
    pillow_heif.from_pillow(im16).save(buf, quality=-1)
    heif_image = pillow_heif.open_heif(BytesIO(buf.getvalue()), convert_hdr_to_8bit=False, pillow_layout=True)[0]
    assert heif_image.mode == "I;16"
    im = heif_image.to_pillow()
    assert borrowed(im)  # `fromarrow` accepts only the `int16` format it uses for `I;16` itself
    expected = Image.frombytes("I;16", heif_image.size, heif_image.data, "raw", "I;16", heif_image.stride)
    helpers.assert_image_equal(im, expected)
    arr = np.asarray(heif_image)
    assert arr.dtype == np.uint16
    assert np.array_equal(arr, np.asarray(expected))


def test_16bit_color_is_not_borrowable():
    # Pillow has no 16-bit multichannel modes, only the single channel `I;16` plane can be borrowed
    heif_image = pillow_heif.open_heif(
        Path("images/heif/RGB_10__128x128.heif"), convert_hdr_to_8bit=False, pillow_layout=True
    )[0]
    heif_image.load()
    assert heif_image.mode == "RGB;16"
    assert heif_image._c_image.plane_channels == 3  # `pillow_layout` widens only 8-bit `RGB`
    assert "arrow_array" in repr(heif_image.__arrow_c_array__()[1])  # other Arrow consumers still can
    with pytest.raises(ValueError):
        heif_image.to_pillow()  # as it always was: there is no Pillow mode for it


def test_arrow_interface_needs_a_decoded_image():
    # `from_pillow` keeps the data it was given, there is no decoded plane to share
    heif_image = pillow_heif.from_pillow(Image.new("RGB", (8, 8)))[0]
    with pytest.raises(ValueError, match="decoded from a file"):
        heif_image.__arrow_c_array__()
    with pytest.raises(ValueError, match="decoded from a file"):
        heif_image.__arrow_c_schema__()
    helpers.assert_image_equal(heif_image.to_pillow(), Image.new("RGB", (8, 8)))


def test_to_pillow_copies_a_padded_pillow_layout_plane():
    # four bytes per pixel but with padding between the rows, so it has to be copied as "RGBX"
    data = encoded("RGB", (101, 64))
    heif_image = pillow_heif.open_heif(BytesIO(data), remove_stride=False, pillow_layout=True)[0]
    heif_image.load()
    assert heif_image._c_image.plane_channels == 4
    assert heif_image.stride != heif_image.size[0] * 4
    im = heif_image.to_pillow()
    assert not borrowed(im)
    helpers.assert_image_equal(im, pillow_heif.open_heif(BytesIO(data))[0].to_pillow())


def test_to_pillow_copies_a_padded_three_byte_plane():
    # 48 pixels are 144 bytes, which `libheif` pads to exactly 48*4: the stride of the Pillow layout, but not its plane
    data = encoded("RGB", (48, 64))
    heif_image = pillow_heif.open_heif(BytesIO(data), remove_stride=False)[0]
    heif_image.load()
    assert heif_image.stride == 48 * 4
    assert heif_image._c_image.plane_channels == 3
    im = heif_image.to_pillow()
    assert not borrowed(im)
    helpers.assert_image_equal(im, pillow_heif.open_heif(BytesIO(data))[0].to_pillow())


def test_arrow_c_array_rejects_a_padded_plane():
    # 101 pixels are 404 bytes, which `libheif` pads to its 16 byte alignment: nothing flat to export
    heif_image = pillow_heif.open_heif(BytesIO(encoded("RGB", (101, 64))), remove_stride=False, pillow_layout=True)[0]
    heif_image.load()
    assert heif_image.stride != heif_image.size[0] * 4
    with pytest.raises(ValueError, match="padded"):
        heif_image.__arrow_c_array__()


def test_plugin_frames_match_the_heif_file():
    path = Path("images/heif/zPug_3.heic")
    heif_file = pillow_heif.open_heif(path)
    im = Image.open(path)
    for index, frame in enumerate(ImageSequence.Iterator(im)):
        frame.load()
        assert borrowed(frame)
        assert frame.mode == heif_file[index].mode
        helpers.assert_image_equal(frame, heif_file[index].to_pillow())


def test_borrowed_image_saves_and_converts():
    data = encoded("RGB", (128, 64))
    im = Image.open(BytesIO(data))
    im.load()
    expected = pillow_heif.open_heif(BytesIO(data))[0].to_pillow()
    helpers.assert_image_equal(im.convert("L"), expected.convert("L"))
    helpers.assert_image_equal(im.resize((64, 32)), expected.resize((64, 32)))
    buf = BytesIO()
    im.save(buf, format="HEIF", quality=-1, chroma=444)
    buf.seek(0)
    helpers.assert_image_equal(Image.open(buf), Image.open(BytesIO(data)))
