from io import BytesIO

import helpers
import pytest
from packaging.version import parse as parse_version
from PIL import Image

import pillow_heif

np = pytest.importorskip("numpy", reason="NumPy not installed")

pillow_heif.register_heif_opener()
if not helpers.hevc_enc():
    pytest.skip(reason="Requires HEIF encoder.", allow_module_level=True)

# Creating HEIF file in memory with 1 image and 3 thumbnails.
im_pillow = Image.effect_mandelbrot((512, 512), (-3, -2.5, 2, 2.5), 100)
im_heif = pillow_heif.from_pillow(im_pillow)
pillow_heif.add_thumbnails(im_heif, boxes=[192, 128, 64])
heif_buf = BytesIO()
im_heif.save(heif_buf)


@pytest.mark.parametrize("im_size", ((256, 128), (127, 64), (63, 64), (31, 32), (20, 100), (14, 16), (11, 16)))
@pytest.mark.parametrize("mode", ("L", "RGB", "RGBA", "I;16"))
def test_numpy_array(im_size, mode):
    im = im_pillow.convert(mode=mode)
    heif_file = pillow_heif.from_pillow(im)
    pil_array = np.asarray(im)
    heif_array = np.asarray(heif_file[0])
    assert np.array_equal(pil_array, heif_array)
    assert np.array_equal(pil_array, np.asarray(heif_file))


@pytest.mark.skipif(parse_version(np.__version__) < parse_version("1.23.0"), reason="Requires numpy >= 1.23")
def test_numpy_array_pillow_thumbnail():
    pil_img = Image.open(heif_buf)
    thumbnail = pillow_heif.thumbnail(pil_img)
    assert thumbnail.size != pil_img.size
    np.asarray(thumbnail)
    for i in range(3):
        np.asarray(pil_img.info["thumbnails"][i])
    pil_img.load()
    for i in range(3):
        with pytest.raises(ValueError):
            np.asarray(pil_img.info["thumbnails"][i])


def test_numpy_array_heif_thumbnail():
    heif_file = pillow_heif.open_heif(heif_buf)
    thumbnail = pillow_heif.thumbnail(heif_file)
    assert thumbnail.size != heif_file.size
    np.asarray(thumbnail)
    for i in range(3):
        np.asarray(heif_file.thumbnails[i])
