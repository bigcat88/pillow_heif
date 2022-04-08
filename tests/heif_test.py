import builtins
import os
from gc import collect
from io import SEEK_END, BytesIO
from pathlib import Path
from sys import platform
from warnings import warn

import pytest

from pillow_heif import (
    HeifChroma,
    HeifColorspace,
    HeifError,
    HeifErrorCode,
    HeifFile,
    HeifImage,
    HeifSaveMask,
    open_heif,
    options,
    register_heif_opener,
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()

avif_images = [f for f in list(Path().glob("images/avif/*.avif"))] + [f for f in list(Path().glob("images/*.avif"))]
heic_images = [f for f in list(Path().glob("images/nokia/*.heic"))] + [f for f in list(Path().glob("images/*.heic"))]
heif_images = [f for f in list(Path().glob("images/*.hif"))] + [f for f in list(Path().glob("images/*.heif"))]

if not options().avif:
    warn("Skipping tests for `AV1` format due to lack of codecs.")
    avif_images.clear()

images_dataset = heic_images + avif_images + heif_images


@pytest.mark.parametrize("img_path", list(Path().glob("images/invalid/*")))
def test_corrupted_open(img_path):
    for input_type in [img_path.read_bytes(), BytesIO(img_path.read_bytes()), img_path, builtins.open(img_path, "rb")]:
        try:
            open_heif(input_type).load()
            assert False
        except HeifError as exception:
            assert exception.code == HeifErrorCode.INVALID_INPUT
            assert repr(exception).find("HeifErrorCode.INVALID_INPUT") != -1
            assert str(exception).find("Invalid input") != -1


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_get_img_thumb_mask_for_save():
    heif_file = open_heif(Path("images/pug_2_2.heic"))
    mask = heif_file.get_img_thumb_mask_for_save(HeifSaveMask.SAVE_NONE)
    output = BytesIO()
    heif_file.save(output, save_mask=mask, quality=10)
    with pytest.raises(HeifError):
        open_heif(output)
    mask = heif_file.get_img_thumb_mask_for_save(HeifSaveMask.SAVE_ONE)
    output = BytesIO()
    heif_file.save(output, save_mask=mask, quality=10)
    new_heif = open_heif(output)
    assert len(new_heif) == 1
    assert len(new_heif[0].thumbnails) == 0
    mask = heif_file.get_img_thumb_mask_for_save(HeifSaveMask.SAVE_ALL)
    output = BytesIO()
    heif_file.save(output, save_mask=mask, quality=10)
    new_heif = open_heif(output)
    assert len(new_heif) == 2
    assert len(new_heif[1].thumbnails) == 1
    mask = heif_file.get_img_thumb_mask_for_save(HeifSaveMask.SAVE_ALL, thumb_box=-1)
    output = BytesIO()
    heif_file.save(output, save_mask=mask, quality=10)
    new_heif = open_heif(output)
    assert len(new_heif) == 2
    assert len(new_heif[1].thumbnails) == 0
    mask = heif_file.get_img_thumb_mask_for_save(HeifSaveMask.SAVE_ALL, thumb_box=128)
    output = BytesIO()
    heif_file.save(output, save_mask=mask, quality=10)
    new_heif = open_heif(output)
    assert len(new_heif) == 2
    assert len(new_heif[1].thumbnails) == 1


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
@pytest.mark.parametrize(
    "thumbs,expected",
    (
        ([0], 1),
        ([1], 1),
        ([256], 1),
        ([128], 2),
        ([128, 0], 2),
        ([0, 128], 2),
        ([128, 400], 3),
    ),
)
def test_add_thumbs_to_mask(thumbs, expected):
    heif_file = open_heif(Path("images/pug_1_1.heic"))
    mask = heif_file.get_img_thumb_mask_for_save(HeifSaveMask.SAVE_ALL)
    output = BytesIO()
    heif_file.add_thumbs_to_mask(mask, thumbs)
    heif_file.save(output, save_mask=mask, quality=10)
    assert len(open_heif(output)[0].thumbnails) == expected


def test_image_index():
    heif_file = open_heif(Path("images/pug_2_2.heic"))
    with pytest.raises(IndexError):
        heif_file[-1].load()
    with pytest.raises(IndexError):
        heif_file[len(heif_file)].load()
    assert heif_file[0].info["main"]
    assert not heif_file[len(heif_file) - 1].info["main"]
    heif_file.close()


@pytest.mark.parametrize("img_path", avif_images[:4] + heic_images[:4])
def test_inputs(img_path):
    with builtins.open(img_path, "rb") as f:
        d = f.read()
        for heif_file in (open_heif(f), open_heif(d), open_heif(bytearray(d)), open_heif(BytesIO(d))):
            assert heif_file.size[0] > 0
            assert heif_file.size[1] > 0
            assert heif_file.info
            assert len(heif_file.data) > 0
            heif_file.load(everything=True)
            heif_file.close(only_fp=True)
            heif_file.close(only_fp=True)
            collect()
            for thumb in heif_file.thumbnails_all():
                assert len(thumb.data) > 0
                thumb.close()
                assert not thumb.data
            heif_file.close()
            assert getattr(heif_file, "_heif_ctx") is None
            assert not heif_file.data
            for thumb in heif_file.thumbnails_all():
                assert not thumb.data
            heif_file.close()
        f.seek(0)


@pytest.mark.parametrize("img_path", avif_images[:4] + heic_images[:4])
def test_inputs_collect(img_path):
    with builtins.open(img_path, "rb") as f:
        d = f.read()
        for heif_file in (open_heif(f), open_heif(d), open_heif(BytesIO(d))):
            heif_file.load(everything=True)
            heif_file.close(only_fp=True)
            heif_file.unload()
            collect()
            with pytest.raises(HeifError):
                assert heif_file.data
            heif_file.close()
        f.seek(0)


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
def test_thumbnails():
    heif_file = open_heif(Path("images/pug_2_3.heic"))
    assert len([_ for _ in heif_file.thumbnails_all(one_for_image=True)]) == 2
    assert len([_ for _ in heif_file.thumbnails_all()]) == 3
    heif_file.load(everything=True)
    heif_file_to_add = open_heif(Path("images/pug_1_1.heic"))
    heif_file.add_from_heif(heif_file_to_add)
    heif_file.close(only_fp=True)
    collect()
    out_buf = BytesIO()
    heif_file.save(out_buf)
    out_heif = open_heif(out_buf)
    assert len([_ for _ in out_heif.thumbnails_all(one_for_image=True)]) == 3
    assert len([_ for _ in out_heif.thumbnails_all()]) == 4
    out_heif.close()
    heif_file.close()


def test_add_from_heif():
    def check_equality():
        assert len(heif_file) == 4
        assert len([_ for _ in heif_file.thumbnails_all()]) == 6
        assert heif_file[0].size == heif_file[1].size
        assert heif_file[0].mode == heif_file[1].mode
        assert heif_file[0].stride == heif_file[1].stride
        assert len(heif_file[0].data) == len(heif_file[1].data)
        assert heif_file[2].size == heif_file[3].size
        assert heif_file[2].mode == heif_file[3].mode
        assert heif_file[2].stride == heif_file[3].stride
        assert len(heif_file[2].data) == len(heif_file[3].data)

    heif_file = open_heif(Path("images/pug_1_1.heic"))
    heif_file.add_from_heif(heif_file)
    assert len(heif_file) == 2
    assert len([_ for _ in heif_file.thumbnails_all()]) == 2
    heif_file_to_add = open_heif(Path("images/pug_1_2.heic"))
    heif_file.add_from_heif(heif_file_to_add)
    heif_file.add_from_heif(heif_file_to_add[0])
    check_equality()
    if options().hevc_enc:
        out_buf = BytesIO()
        heif_file.save(out_buf, quality=10, enc_params=[("x265:ctu", "32")])
        heif_file.close()
        heif_file_to_add.close()
        heif_file = open_heif(out_buf)
        assert len(heif_file) == 4
        assert len([_ for _ in heif_file.thumbnails_all()]) == 6
        heif_file.load(everything=True)
        check_equality()


@pytest.mark.skipif(platform.lower() == "win32", reason="No 10/12 bit encoder for Windows.")
def test_add_from_heif_10bit():
    def check_equality():
        assert len(heif_file) == 4
        assert heif_file[0].size == heif_file[1].size
        assert heif_file[0].mode == heif_file[1].mode
        assert heif_file[0].stride == heif_file[1].stride
        assert len(heif_file[0].data) == len(heif_file[1].data)
        assert heif_file[2].size == heif_file[3].size
        assert heif_file[2].mode == heif_file[3].mode
        assert heif_file[2].stride == heif_file[3].stride
        assert len(heif_file[2].data) == len(heif_file[3].data)

    heif_file = open_heif(Path("images/mono10bit.heif"), convert_hdr_to_8bit=False)
    heif_file.add_from_heif(heif_file)
    assert len(heif_file) == 2
    heif_file_to_add = open_heif(Path("images/rgba10bit.heif"), convert_hdr_to_8bit=False)
    heif_file.add_from_heif(heif_file_to_add)
    heif_file.add_from_heif(heif_file_to_add[0])
    check_equality()
    out_buf = BytesIO()
    if options().hevc_enc:
        heif_file.save(out_buf, enc_params=[("x265:ctu", "32")])
        heif_file.close()
        heif_file_to_add.close()
        heif_file = open_heif(out_buf, convert_hdr_to_8bit=False)
        assert len(heif_file) == 4
        heif_file.load(everything=True)
        check_equality()


def test_collect():
    heif_file = open_heif(Path("images/pug_2_1.heic"))
    collect()
    heif_file.load(everything=True)
    heif_file.unload(everything=True)
    collect()
    heif_file.load(everything=True)
    heif_file.close(only_fp=True)
    collect()
    if options().hevc_enc:
        new_heif_image = BytesIO()
        heif_file.save(new_heif_image, quality=10)
        assert isinstance(open_heif(new_heif_image), HeifFile)
    for image in heif_file:
        data = image.data  # noqa
        for thumbnail in image.thumbnails:
            data = thumbnail.data  # noqa
            thumbnail.close()
            collect()
    for image in heif_file:
        data = image.data  # noqa
        image.close()
    collect()
    for image in heif_file:
        image.load()
        assert not getattr(image, "_img_data", None)
        for thumbnail in image.thumbnails:
            thumbnail.load()
            assert not getattr(image, "_img_data", None)
    heif_file.close()


@pytest.mark.parametrize("image_path", images_dataset)
def test_all(image_path):
    heif_file = open_heif(image_path)
    for c, image in enumerate(heif_file):
        image.misc["to_8bit"] = True
        pass_count = 2 if heif_file.bit_depth > 8 and platform.lower() != "win32" else 1
        for i in range(pass_count):
            if i == 1:
                image.misc["to_8bit"] = False
                image.unload()
            assert min(image.size) > 0
            assert image.size[1] > 0
            assert image.mode == "RGBA" if image.has_alpha else "RGB"
            assert image.bit_depth >= 8
            assert image.chroma == HeifChroma.UNDEFINED
            assert image.color == HeifColorspace.UNDEFINED

            minimal_stride = image.size[0] * 4 if image.has_alpha else image.size[0] * 3
            if image.bit_depth > 8 and not image.misc["to_8bit"]:
                minimal_stride *= 2
            assert image.stride >= minimal_stride
            assert len(image.data) == image.stride * image.size[1]
            assert image.chroma != HeifChroma.UNDEFINED
            assert image.color == HeifColorspace.RGB
            assert isinstance(image.load(), HeifImage)

            if not options().hevc_enc:
                continue
            save_mask = heif_file.get_img_thumb_mask_for_save(mask=HeifSaveMask.SAVE_NONE)
            save_mask[c][0] = True
            new_heif_image = BytesIO()
            heif_file.save(new_heif_image, quality=10, save_mask=save_mask)
            new_heif_file = open_heif(new_heif_image, convert_hdr_to_8bit=image.misc["to_8bit"])
            assert new_heif_file.mode == image.mode
            assert new_heif_file.bit_depth == 8 if image.misc["to_8bit"] else image.bit_depth
            assert isinstance(new_heif_file.load(), HeifFile)
            assert new_heif_file.has_alpha == image.has_alpha
            assert new_heif_file.chroma == image.chroma
            assert new_heif_file.color == image.color
            assert new_heif_file.size[0] == image.size[0]
            assert new_heif_file.size[1] == image.size[1]
            minimal_stride = new_heif_file.size[0] * 4 if new_heif_file.has_alpha else new_heif_file.size[0] * 3
            if new_heif_file.bit_depth > 8 and not new_heif_file[0].misc["to_8bit"]:
                minimal_stride *= 2
            assert new_heif_file.stride >= minimal_stride
            new_heif_file.close()
