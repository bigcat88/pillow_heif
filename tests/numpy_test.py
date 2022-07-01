# With Numpy we test interface support(asarray)

import os
from pathlib import Path

import pytest
from PIL import Image

import pillow_heif

np = pytest.importorskip("numpy", reason="NumPy not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pillow_heif.register_heif_opener()


@pytest.mark.parametrize(
    "img_path, modes",
    (
        ("images/rgba10.heif", ("L", "RGBA")),
        ("images/rgb8_512_512_1_0.heic", ("L", "RGB", "RGBA")),
        ("images/rgb8_150_128_2_1.heic", ("L", "RGB", "RGBA")),
        ("images/jpeg_gif_png/I_color_mode_image.pgm", ("I;16", "L", "RGB", "RGBA")),
    ),
)
def test_numpy_array(img_path, modes):
    pil_img = Image.open(Path(img_path))
    for mode in modes:
        converted_pil_img = pil_img.convert(mode=mode)
        heif_file = pillow_heif.from_pillow(converted_pil_img)
        pil_array = np.asarray(converted_pil_img)
        heif_array = np.asarray(heif_file[0])
        assert np.array_equal(pil_array, heif_array)
