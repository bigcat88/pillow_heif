import builtins
import os
from io import SEEK_END, BytesIO
from pathlib import Path
from sys import platform

import pytest
from heif_test import compare_heif_files_fields

from pillow_heif import _options  # noqa
from pillow_heif import HeifError, open_heif, options, register_heif_opener

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_outputs():
    with builtins.open(Path("images/pug_1_1.heic"), "rb") as f:
        output = BytesIO()
        open_heif(f).save(output, quality=10)
        assert output.seek(0, SEEK_END) > 0
        with builtins.open(Path("tmp.heic"), "wb") as output:
            open_heif(f).save(output, quality=10)
            assert output.seek(0, SEEK_END) > 0
        open_heif(f).save(Path("tmp.heic"), quality=10)
        assert Path("tmp.heic").stat().st_size > 0
        Path("tmp.heic").unlink()
        with pytest.raises(TypeError):
            open_heif(f).save(bytes(b"1234567890"), quality=10)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_save_empty():
    heic_file = open_heif(Path("images/pug_1_0.heic"))
    del heic_file[0]
    out_buffer = BytesIO()
    with pytest.raises(ValueError):
        heic_file.save(out_buffer)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
@pytest.mark.parametrize(
    "image_path,remove_img,remove_thumb,expected",
    (
        ("images/pug_2_1.heic", [0], [], (1, 0)),
        ("images/pug_2_1.heic", [1], [], (1, 1)),
        ("images/pug_2_1.heic", [1], [(0, 0)], (1, 0)),
        ("images/pug_2_3.heic", [0], [], (1, 2)),
        ("images/pug_2_3.heic", [0], [(0, 0)], (1, 1)),
        ("images/pug_2_3.heic", [0], [(0, 1)], (1, 1)),
        ("images/pug_2_3.heic", [0], [(0, 1), (0, 0)], (1, 0)),
        ("images/pug_2_3.heic", [1], [], (1, 1)),
        ("images/pug_2_3.heic", [1], [(0, 0)], (1, 0)),
    ),
)
def test_remove(image_path, remove_img: list, remove_thumb: list, expected: tuple):
    heic_file_2_images = open_heif(Path(image_path))
    for remove_index in remove_img:
        del heic_file_2_images[remove_index]
    for remove_tuple in remove_thumb:
        del heic_file_2_images[remove_tuple[0]].thumbnails[remove_tuple[1]]
    out_buffer = BytesIO()
    heic_file_2_images.save(out_buffer)
    heic_file_1_image = open_heif(out_buffer)
    assert len(heic_file_1_image) == expected[0]
    assert len(heic_file_1_image.thumbnails) == expected[1]


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
@pytest.mark.parametrize(
    "thumbs,expected",
    (
        (-1, 1),
        ([-1], 1),
        (0, 1),
        ([0], 1),
        (1, 1),
        ([1], 1),
        (256, 1),
        ([256], 1),
        ([2048], 1),
        (128, 2),
        ([128], 2),
        ([128, 0], 2),
        ([0, 128], 2),
        ([128, 400], 3),
    ),
)
def test_add_thumbs_to_image(thumbs, expected):
    heif_file = open_heif(Path("images/pug_1_1.heic"))
    heif_file[0].add_thumbnails(thumbs)
    output = BytesIO()
    heif_file.save(output, quality=10)
    assert len(open_heif(output)[0].thumbnails) == expected


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
@pytest.mark.parametrize(
    "thumbs,expected",
    (
        ([-1], (1, 0)),
        (0, (1, 0)),
        (256, (2, 1)),
        ([256], (2, 1)),
        (128, (1, 1)),
        ([128, 0], (1, 1)),
        ([0, 128], (1, 1)),
        ([128, 400], (2, 2)),
        ([280, 464], (3, 2)),
    ),
)
def test_add_thumbs_to_images(thumbs, expected):
    heif_file = open_heif(Path("images/pug_2_1.heic"))
    heif_file.add_thumbnails(thumbs)
    output = BytesIO()
    heif_file.save(output, quality=10)
    heif_file = open_heif(output)
    assert len(heif_file[0].thumbnails) == expected[0]
    assert len(heif_file[1].thumbnails) == expected[1]


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_add_from_heif():
    heif_file = open_heif(Path("images/pug_1_1.heic"))
    heif_file.add_from_heif(heif_file)
    assert len(heif_file) == 2
    assert len([_ for _ in heif_file.thumbnails_all()]) == 2
    compare_heif_files_fields(heif_file[0], heif_file[1])
    heif_file_to_add = open_heif(Path("images/pug_1_2.heic"))
    heif_file.add_from_heif(heif_file_to_add)
    heif_file.add_from_heif(heif_file_to_add[0])
    compare_heif_files_fields(heif_file[2], heif_file[3])
    out_buf = BytesIO()
    heif_file.save(out_buf, quality=10, enc_params=[("x265:ctu", "32")])
    heif_file_to_add.close()
    saved_heif_file = open_heif(out_buf)
    assert len(saved_heif_file) == 4
    assert len([_ for _ in saved_heif_file.thumbnails_all()]) == 6
    compare_heif_files_fields(heif_file, saved_heif_file, ignore=["len"])


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
@pytest.mark.skipif(platform.lower() == "win32", reason="No 10/12 bit encoder for Windows.")
def test_10_bit():
    heif_file = open_heif(Path("images/mono10bit.heif"), convert_hdr_to_8bit=False)
    heif_file.add_from_heif(heif_file)
    assert len(heif_file) == 2
    compare_heif_files_fields(heif_file[0], heif_file[1])
    heif_file_to_add = open_heif(Path("images/rgba10bit.heif"), convert_hdr_to_8bit=False)
    heif_file.add_from_heif(heif_file_to_add)
    heif_file.add_from_heif(heif_file_to_add[0])
    compare_heif_files_fields(heif_file[2], heif_file[3])
    out_buf = BytesIO()
    heif_file.save(out_buf, enc_params=[("x265:ctu", "32")])
    heif_file.close()
    heif_file_to_add.close()
    heif_file = open_heif(out_buf, convert_hdr_to_8bit=False)
    assert len(heif_file) == 4
    compare_heif_files_fields(heif_file[0], heif_file[1])
    compare_heif_files_fields(heif_file[2], heif_file[3])
    assert heif_file[0].bit_depth == 10
    assert heif_file[0].mode == "RGBA"
    assert heif_file[2].bit_depth == 10
    assert heif_file[2].mode == "RGBA"


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_save_all():
    heif_file = open_heif(Path("images/pug_2_0.heic"))
    out_buf_save_all = BytesIO()
    heif_file.save(out_buf_save_all, save_all=True, quality=15)
    out_buf_save_one = BytesIO()
    heif_file.save(out_buf_save_one, save_all=False, quality=15)
    assert len(open_heif(out_buf_save_all)) == 2
    assert len(open_heif(out_buf_save_one)) == 1


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_hif_file():
    heif_file1 = open_heif(Path("images/cat.hif"))
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=10)
    heif_file2 = open_heif(out_buf)
    compare_heif_files_fields(heif_file1, heif_file2, thumb_max_differ=3)


def test_no_encoder():
    try:
        _options.CFG_OPTIONS._hevc_enc = False
        heic_file = open_heif(Path("images/pug_1_0.heic"))
        out_buffer = BytesIO()
        with pytest.raises(HeifError):
            heic_file.save(out_buffer)
    finally:
        _options.CFG_OPTIONS = _options.PyLibHeifOptions()
