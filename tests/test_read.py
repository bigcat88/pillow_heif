import io
import os
from pathlib import Path
import piexif
import pytest
from PIL import Image, ImageCms
import pillow_heif


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_check_filetype(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    filetype = pillow_heif.check(fn)
    assert pillow_heif.heif_filetype_no != filetype


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_paths(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    heif_file = pillow_heif.read(fn)
    assert heif_file is not None
    width, height = heif_file.size
    assert width > 0
    assert height > 0
    assert heif_file.brand != pillow_heif.constants.heif_brand_unknown_brand
    assert len(heif_file.data) > 0


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_file_objects(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    with open(fn, "rb") as f:
        heif_file = pillow_heif.read(f)
        assert heif_file is not None
        width, height = heif_file.size
        assert width > 0
        assert height > 0
        assert heif_file.brand != pillow_heif.constants.heif_brand_unknown_brand
        assert len(heif_file.data) > 0


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_bytes(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    with open(fn, "rb") as f:
        d = f.read()
        heif_file = pillow_heif.read(d)
        assert heif_file is not None
        width, height = heif_file.size
        assert width > 0
        assert height > 0
        assert heif_file.brand != pillow_heif.constants.heif_brand_unknown_brand
        assert len(heif_file.data) > 0


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_bytearrays(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    with open(fn, "rb") as f:
        d = f.read()
        d = bytearray(d)
        heif_file = pillow_heif.read(d)
        assert heif_file is not None
        width, height = heif_file.size
        assert width > 0
        assert height > 0
        assert heif_file.brand != pillow_heif.constants.heif_brand_unknown_brand
        assert len(heif_file.data) > 0


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_exif_metadata(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    heif_file = pillow_heif.read(fn)
    for m in heif_file.metadata or []:
        if m["type"] == "Exif":
            exif_dict = piexif.load(m["data"])
            assert "0th" in exif_dict
            assert len(exif_dict["0th"]) > 0
            assert "Exif" in exif_dict
            assert len(exif_dict["Exif"]) > 0


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_icc_color_profile(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    heif_file = pillow_heif.read(fn)
    if heif_file.color_profile and heif_file.color_profile["type"] in ["prof", "rICC", ]:
        profile = io.BytesIO(heif_file.color_profile["data"])
        cms = ImageCms.getOpenProfile(profile)


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_pillow_frombytes(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    heif_file = pillow_heif.read(fn)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_10_bit(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    heif_file = pillow_heif.read(fn)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
