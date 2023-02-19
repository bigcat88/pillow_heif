from io import BytesIO
from typing import Tuple

import helpers
import pytest
from packaging.version import parse as parse_version
from PIL import Image

import pillow_heif

np = pytest.importorskip("numpy", reason="NumPy not installed")
if parse_version(np.__version__) < parse_version("1.23.0"):
    pytest.skip(reason="Requires numpy >= 1.23", allow_module_level=True)

pillow_heif.register_heif_opener()
if not helpers.hevc_enc():
    pytest.skip(reason="Requires HEVC encoder.", allow_module_level=True)

# Creating HEIF file in memory with 1 image.
im_pillow = Image.effect_mandelbrot((512, 512), (-3, -2.5, 2, 2.5), 100)
im_heif = pillow_heif.from_pillow(im_pillow)
heif_buf = BytesIO()
im_heif.save(heif_buf)


@pytest.mark.parametrize("mode", ("L", "LA", "RGB", "RGBA", "I;16"))
@pytest.mark.parametrize("im_size", ((256, 128), (127, 64), (63, 64), (31, 32), (20, 100), (14, 16), (11, 16), (1, 1)))
def test_numpy_array(im_size: Tuple, mode):
    im = im_pillow.resize(im_size).convert(mode=mode)
    heif_file = pillow_heif.from_pillow(im)
    pil_array = np.asarray(im)
    heif_array = np.asarray(heif_file[0])
    assert np.array_equal(pil_array, heif_array)
    assert np.array_equal(pil_array, np.asarray(heif_file))
