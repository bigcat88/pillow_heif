import gc
import io
import os
from pathlib import Path

import piexif
import pytest
from PIL import Image, ImageCms
import pillow_heif


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(TESTS_DIR)

heic_files = list(Path().glob('images/**/*.heic'))
hif_files = list(Path().glob('images/**/*.HIF'))
avif_files = list(Path().glob('images/**/*.avif'))
heif_files = heic_files + hif_files + avif_files


@pytest.mark.parametrize('path', heif_files)
def test_check(path):
    filetype = pillow_heif.check(path)
    assert pillow_heif.heif_filetype_no != filetype
    unsupported_list = ['rally_burst.heic', 'bird_burst.heic', 'starfield_animation.heic', 'sea1_animation.heic']
    if os.path.basename(path) in unsupported_list:
        assert pillow_heif.heif_filetype_yes_unsupported == filetype
    else:
        assert pillow_heif.heif_filetype_yes_unsupported != filetype


@pytest.mark.parametrize('path', heif_files[:2])
def test_get_bytes_from_path(path):
    d = pillow_heif.reader._get_bytes(path)
    assert d == path.read_bytes()


@pytest.mark.parametrize('path', heif_files[:2])
def test_get_bytes_from_file_name(path):
    d = pillow_heif.reader._get_bytes(str(path))
    assert d == path.read_bytes()


@pytest.mark.parametrize('path', heif_files[:2])
def test_get_bytes_from_file_object(path):
    with open(path, 'rb') as f:
        d = pillow_heif.reader._get_bytes(f)
    assert d == path.read_bytes()


@pytest.mark.parametrize('path', heif_files[:2])
def test_get_bytes_from_bytes(path):
    with open(path, 'rb') as f:
        d = pillow_heif.reader._get_bytes(f.read())
    assert d == path.read_bytes()


@pytest.mark.parametrize('path', heif_files[:2])
def test_get_bytes_from_bytes(path):
    with open(path, 'rb') as f:
        d = pillow_heif.reader._get_bytes(bytearray(f.read()))
    assert d == path.read_bytes()


@pytest.fixture(scope="session", params=heif_files)
def heif_file(request):
    return pillow_heif.read(request.param)


@pytest.mark.parametrize('path', heif_files)
def test_open_and_load(path):
    heif_file = pillow_heif.open(path)
    assert heif_file.size[0] > 0
    assert heif_file.size[1] > 0
    assert heif_file.has_alpha is not None
    assert heif_file.mode is not None
    assert heif_file.bit_depth is not None

    assert heif_file.data is None
    assert heif_file.stride is None

    if path.name == 'arrow.heic':
        assert heif_file.metadata
        assert heif_file.color_profile

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


@pytest.mark.parametrize('path', heif_files)
def test_open_and_load_data_not_collected(path):
    data = path.read_bytes()
    heif_file = pillow_heif.open(data)
    data = None  # heif_file.load() should work even if there is no other refs to the source data.
    gc.collect()
    heif_file.load()


def to_pillow_image(heif_file):
    return Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        'raw',
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
def test_read_bytes(folder, image_name):
    fn = os.path.join(TESTS_DIR, 'images', folder, image_name)
    with open(fn, 'rb') as f:
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
    with open(fn, 'rb') as f:
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
        if m['type'] == 'Exif':
            exif_dict = piexif.load(m['data'])
            assert '0th' in exif_dict
            assert len(exif_dict['0th']) > 0
            assert 'Exif' in exif_dict
            assert len(exif_dict['Exif']) > 0


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
        assert heif_file.color_profile['type'] is expected_color_profile
    else:
        assert heif_file.color_profile is None
        return
    if heif_file.color_profile and heif_file.color_profile['type'] in ['prof', 'rICC', ]:
        profile = io.BytesIO(heif_file.color_profile['data'])
        _cms = ImageCms.getOpenProfile(profile)


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
    _image = to_pillow_image(heif_file)
