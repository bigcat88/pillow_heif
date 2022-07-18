import builtins
import gc
import os
from io import SEEK_END, BytesIO
from pathlib import Path
from unittest import mock

import pytest
from helpers import compare_hashes, compare_heif_files_fields, create_heif
from PIL import Image

from pillow_heif import (
    HeifError,
    HeifFile,
    from_pillow,
    open_heif,
    options,
    register_heif_opener,
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()

if not options().hevc_enc:
    pytest.skip("No HEVC encoder.", allow_module_level=True)

pytest.importorskip("numpy", reason="NumPy not installed")


def test_outputs():
    heif_file = open_heif(create_heif((31, 64)))
    output = BytesIO()
    heif_file.save(output, quality=10)
    assert output.seek(0, SEEK_END) > 0
    with builtins.open(Path("tmp.heic"), "wb") as output:
        heif_file.save(output, quality=10)
        assert output.seek(0, SEEK_END) > 0
    heif_file.save(Path("tmp.heic"), quality=10)
    assert Path("tmp.heic").stat().st_size > 0
    Path("tmp.heic").unlink()
    with pytest.raises(TypeError):
        heif_file.save(bytes(b"1234567890"), quality=10)


def test_add_from():
    heif_file1_buf = create_heif()
    heif_file1 = open_heif(heif_file1_buf)
    heif_file2_buf = create_heif((210, 128), thumb_boxes=[48, 32], n_images=2)
    heif_file2 = open_heif(heif_file2_buf)
    heif_file1.add_from_heif(heif_file2, load_one=True)
    heif_file1.add_from_heif(heif_file2[1], load_one=True)
    heif_file1.add_from_heif(heif_file2[1])
    gc.collect()
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=100)
    out_heif = open_heif(out_buf)
    assert len(out_heif) == 4
    assert len(list(out_heif.thumbnails_all(one_for_image=True))) == 3
    assert len(list(out_heif.thumbnails_all(one_for_image=False))) == 6
    compare_heif_files_fields(heif_file1[0], out_heif[0])
    compare_heif_files_fields(heif_file2[0], out_heif[1])
    compare_heif_files_fields(heif_file2[1], out_heif[2])
    compare_heif_files_fields(heif_file2[1], out_heif[3])
    pillow_image = Image.open(out_buf)
    compare_hashes([pillow_image, heif_file1_buf])
    pillow_image.seek(1)
    pillow_original = Image.open(heif_file2_buf)
    compare_hashes([pillow_image, pillow_original])
    pillow_image.seek(2)
    pillow_original.seek(1)
    compare_hashes([pillow_image, pillow_original], max_difference=1)


def test_remove():
    heif_buf = create_heif((72, 68), thumb_boxes=[32], n_images=2)
    out_buffer = BytesIO()
    # clear list with images
    heif_file = open_heif(heif_buf)
    heif_file.images.clear()
    assert len(heif_file) == 0
    # removing first image
    heif_file = open_heif(heif_buf)
    del heif_file[0]
    heif_file.save(out_buffer)
    _ = open_heif(out_buffer)
    assert len(_) == 1
    assert len(_.thumbnails) == 1
    assert _.size == (36, 34)
    # removing second and first image
    heif_file = open_heif(heif_buf)
    del heif_file[1]
    del heif_file[0]
    assert len(heif_file) == 0


def test_save_all():
    heif_file = open_heif(create_heif((61, 64), n_images=2))
    out_buf = BytesIO()
    heif_file.save(out_buf, save_all=True, quality=15)
    assert len(open_heif(out_buf)) == 2
    heif_file.save(out_buf, save_all=False, quality=15)
    assert len(open_heif(out_buf)) == 1


def test_append_images():
    heif_file = open_heif(create_heif((72, 68), thumb_boxes=[32, 16], n_images=2))
    heif_file2 = open_heif(create_heif((81, 79), thumb_boxes=[32], n_images=2))
    heif_file3 = open_heif(create_heif((51, 49), thumb_boxes=[16], n_images=2))
    out_buf = BytesIO()
    heif_file.save(out_buf, append_images=[heif_file2, heif_file3, heif_file3[1]])
    heif_file_out = open_heif(out_buf)
    assert len([i for i in heif_file_out.thumbnails_all()]) == 4 + 2 + 2 + 1
    assert len(heif_file_out) == 7
    compare_heif_files_fields(heif_file[0], heif_file_out[0])
    compare_heif_files_fields(heif_file[1], heif_file_out[1])
    compare_heif_files_fields(heif_file2[0], heif_file_out[2])
    compare_heif_files_fields(heif_file2[1], heif_file_out[3])
    compare_heif_files_fields(heif_file3[0], heif_file_out[4])
    compare_heif_files_fields(heif_file3[1], heif_file_out[5])


def test_scale():
    heif_buf = create_heif()
    im_heif = open_heif(heif_buf)
    assert im_heif[0].size == (512, 512)
    im_heif.scale(256, 256)
    assert im_heif[0].size == (256, 256)
    out_buffer = BytesIO()
    im_heif.save(out_buffer, quality=-1)
    compare_hashes([heif_buf, out_buffer])


def test_save_empty():
    heic_file = open_heif(create_heif())
    del heic_file[0]
    with pytest.raises(ValueError):
        heic_file.save(BytesIO())


def test_save_empty_with_append():
    out_buffer = BytesIO()
    empty_heif_file = HeifFile()
    heif_file = open_heif(create_heif())
    empty_heif_file.save(out_buffer, append_images=heif_file)
    compare_heif_files_fields(heif_file, open_heif(out_buffer))
    empty_heif_file.save(out_buffer, append_images=heif_file, save_all=False)
    heif_file = open_heif(out_buffer)
    assert len(heif_file) == 1


def test_10_bit():
    heif_file = open_heif(Path("images/mono10.heif"), convert_hdr_to_8bit=False)
    heif_file.add_from_heif(heif_file)
    assert len(heif_file) == 2
    compare_heif_files_fields(heif_file[0], heif_file[1])
    heif_file_to_add = open_heif(Path("images/rgba10.heif"), convert_hdr_to_8bit=False)
    heif_file.add_from_heif(heif_file_to_add)
    heif_file.add_from_heif(heif_file_to_add[0])
    compare_heif_files_fields(heif_file[2], heif_file[3])
    heif_file_to_add = None  # noqa
    gc.collect()
    out_buf = BytesIO()
    heif_file.save(out_buf, enc_params=[("x265:ctu", "32")])
    heif_file = open_heif(out_buf, convert_hdr_to_8bit=False)
    assert len(heif_file) == 4
    compare_heif_files_fields(heif_file[0], heif_file[1])
    compare_heif_files_fields(heif_file[2], heif_file[3])
    assert heif_file[0].bit_depth == 10
    assert heif_file[0].mode == "RGBA;10"
    assert heif_file[2].bit_depth == 10
    assert heif_file[2].mode == "RGBA;10"


def test_hif_file():
    heif_file1 = open_heif(Path("images/etc_heif/cat.hif"))
    assert heif_file1.original_bit_depth == 10
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=10)
    heif_file2 = open_heif(out_buf)
    assert heif_file2.original_bit_depth == 8
    compare_heif_files_fields(heif_file1, heif_file2, ignore=["t_stride", "original_bit_depth"])


@mock.patch("pillow_heif._options.CFG_OPTIONS._hevc_enc", False)
def test_no_encoder():
    im_heif = from_pillow(Image.new("L", (64, 64)))
    out_buffer = BytesIO()
    with pytest.raises(HeifError):
        im_heif.save(out_buffer)
