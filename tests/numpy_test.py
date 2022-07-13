# Testing Numpy interface support(asarray)

import os
from pathlib import Path

import pytest
from packaging.version import parse as parse_version
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


@pytest.mark.skipif(parse_version(np.__version__) < parse_version("1.23.0"), reason="Requires numpy >= 1.23")
def test_numpy_array_thumbnail_pillow():
    pil_img = Image.open(Path("images/rgb8_512_512_1_2.heic"))
    thumbnail = pillow_heif.thumbnail(pil_img)
    assert thumbnail.size != pil_img.size
    np.asarray(thumbnail)
    np.asarray(pil_img.info["thumbnails"][0])
    pil_img.load()
    with pytest.raises(ValueError):
        np.asarray(pil_img.info["thumbnails"][0])


def test_numpy_array_thumbnail_heif():
    heif_file = pillow_heif.open_heif(Path("images/rgb8_512_512_1_2.heic"))
    thumbnail = pillow_heif.thumbnail(heif_file)
    assert thumbnail.size != heif_file.size
    np.asarray(thumbnail)
    np.asarray(heif_file.thumbnails[0])


def test_numpy_array_no_thumbnail_pillow():
    pil_img = Image.open(Path("images/rgb8_512_512_1_0.heic"))
    thumbnail = pillow_heif.thumbnail(pil_img)
    assert thumbnail.size == pil_img.size
    pil_img = Image.open(Path("images/rgb8_512_512_1_2.heic"))
    thumbnail = pillow_heif.thumbnail(pil_img, min_box=1024 * 10)
    assert thumbnail.size == pil_img.size


def test_numpy_array_no_thumbnail_heif():
    heif_file = pillow_heif.open_heif(Path("images/rgb8_512_512_1_0.heic"))
    thumbnail = pillow_heif.thumbnail(heif_file)
    assert thumbnail.size == heif_file.size
    heif_file = pillow_heif.open_heif(Path("images/rgb8_512_512_1_2.heic"))
    thumbnail = pillow_heif.thumbnail(heif_file, min_box=1024 * 10)
    assert thumbnail.size == heif_file.size
