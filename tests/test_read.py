import gc
import io
import os
import piexif
import pytest
from PIL import Image, ImageCms
import pillow_heif


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def to_pillow_image(heif_file):
    return Image.frombytes(
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
    assert pillow_heif.heif_filetype_yes_unsupported != filetype


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
    ['folder', 'image_name', 'expected_color_profile'],
    [
        ('Pug', 'PUG1.HEIC', 'prof',),
        ('Pug', 'PUG2.HEIC', 'prof',),
        ('Pug', 'PUG3.HEIC', None,),
        ('hif', '93FG5559.HIF', 'nclx',),
        ('hif', '93FG5564.HIF', 'nclx',),
    ]
)
def test_read_icc_color_profile(folder, image_name, expected_color_profile):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    heif_file = pillow_heif.read(fn)
    if expected_color_profile:
        assert heif_file.color_profile["type"] is expected_color_profile
    else:
        assert heif_file.color_profile is None
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
    image = to_pillow_image(heif_file)


# @pytest.mark.parametrize(
#     ['folder', 'image_name'],
#     [
#         ('', 'arrow.heic',),
#     ]
# )
# def test_no_transformations(folder, image_name):
#     fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
#     transformed = pillow_heif.read(fn)
#     native = pillow_heif.read(fn, apply_transformations=False)
#     assert transformed.size[0] != transformed.size[1]
#     assert transformed.size == native.size[::-1]
#     transformed = to_pillow_image(transformed)
#     native = to_pillow_image(native)
#     assert transformed == native.transpose(Image.ROTATE_270)


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_read_10_bit__everywhere(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    heif_file = pillow_heif.read(fn)
    image = to_pillow_image(heif_file)


@pytest.mark.parametrize(
    ['folder', 'image_name', 'has_metadata', 'has_profile'],
    [
        ('Pug', 'PUG1.HEIC', True, True,),
        ('Pug', 'PUG3.HEIC', False, False,),
        ('hif', '93FG5559.HIF', True, True,),
    ]
)
def test_open_and_load__everywhere(folder, image_name, has_metadata, has_profile):
    last_metadata = None
    last_color_profile = None
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    heif_file = pillow_heif.open(fn)
    assert heif_file.size[0] > 0
    assert heif_file.size[1] > 0
    assert heif_file.has_alpha is not None
    assert heif_file.mode is not None
    assert heif_file.bit_depth is not None
    assert heif_file.data is None
    assert heif_file.stride is None
    if heif_file.metadata:
        last_metadata = heif_file.metadata[0]
    if heif_file.color_profile:
        last_color_profile = heif_file.color_profile
    res = heif_file.load()
    assert heif_file is res
    assert heif_file.data is not None
    assert heif_file.stride is not None
    assert len(heif_file.data) >= heif_file.stride * heif_file.size[1]
    assert type(heif_file.data[:100]) == bytes
    # Subsequent calls don't change anything
    res = heif_file.load()
    assert heif_file is res
    assert heif_file.data is not None
    assert heif_file.stride is not None
    if has_metadata:
        assert last_metadata is not None
    else:
        assert last_metadata is None
    if has_profile:
        assert last_color_profile is not None
    else:
        assert last_color_profile is None


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('hif', '93FG5559.HIF',),
    ]
)
def test_open_and_load_data_collected__everywhere(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    with open(fn, "rb") as f:
        data = f.read()
    heif_file = pillow_heif.open(data)
    # heif_file.load() should work even if there is no other refs to the source data.
    data = None
    gc.collect()
    heif_file.load()
