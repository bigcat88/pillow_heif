import builtins
import os
from gc import collect
from io import BytesIO
from pathlib import Path
from typing import Union
from warnings import warn

import pytest

from pillow_heif import (
    HeifChroma,
    HeifColorspace,
    HeifError,
    HeifErrorCode,
    HeifFile,
    HeifImage,
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

full_dataset = heic_images + avif_images + heif_images
minimal_dataset = [
    Path("images/pug_1_0.heic"),
    Path("images/pug_2_1.heic"),
    Path("images/invalid_id.heic"),
    Path("images/pug_2_3.heic"),
    Path("images/nokia/alpha.heic"),
]


def compare_heif_files_fields(
    heif1: Union[HeifFile, HeifImage], heif2: Union[HeifFile, HeifImage], ignore=None, thumb_max_differ=0
):
    def compare_images_fields(image1: HeifImage, image2: HeifImage):
        assert image1.size == image2.size
        assert image1.mode == image2.mode
        if ignore is not None and "bit_depth" not in ignore:
            assert image1.bit_depth == image2.bit_depth
        if ignore is not None and "stride" not in ignore:
            assert image1.stride == image2.stride
        if ignore is not None and "len" not in ignore:
            assert len(image1.data) == len(image2.data)
        for i_thumb, thumbnail in enumerate(image1.thumbnails):
            with_difference = thumbnail.size[0] - image2.thumbnails[i_thumb].size[0]
            height_difference = thumbnail.size[1] - image2.thumbnails[i_thumb].size[1]
            assert with_difference + height_difference <= thumb_max_differ
            assert thumbnail.mode == image2.thumbnails[i_thumb].mode
            if ignore is not None and "bit_depth" not in ignore:
                assert thumbnail.bit_depth == image2.thumbnails[i_thumb].bit_depth
            if ignore is not None and "stride" not in ignore:
                assert thumbnail.stride == image2.thumbnails[i_thumb].stride
            if ignore is not None and "len" not in ignore:
                assert len(thumbnail.data) == len(image2.thumbnails[i_thumb].data)

    if isinstance(heif1, HeifFile):
        for i, image in enumerate(heif1):
            compare_images_fields(image, heif2[i])
    else:
        compare_images_fields(heif1, heif2)


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


def test_index():
    heif_file = open_heif(Path("images/pug_2_2.heic"))
    with pytest.raises(IndexError):
        heif_file[-1].load()
    with pytest.raises(IndexError):
        heif_file[len(heif_file)].load()
    assert heif_file[0].info["main"]
    assert not heif_file[len(heif_file) - 1].info["main"]
    with pytest.raises(IndexError):
        heif_file[0].thumbnails[-1].load()
    with pytest.raises(IndexError):
        heif_file[0].thumbnails[len(heif_file[0].thumbnails)].load()
    with pytest.raises(IndexError):
        del heif_file[-1]
    with pytest.raises(IndexError):
        del heif_file[2]
    heif_file.close()


def test_etc():
    heif_file = open_heif(Path("images/pug_2_2.heic"))
    heif_file.load(everything=False)
    assert getattr(heif_file[0], "_img_data")
    assert not getattr(heif_file[1], "_img_data")
    assert heif_file.size == heif_file[0].size
    assert heif_file.mode == heif_file[0].mode
    assert len(heif_file.data) == len(heif_file[0].data)
    assert heif_file.stride == heif_file[0].stride
    assert heif_file.chroma == heif_file[0].chroma
    assert heif_file.color == heif_file[0].color
    assert heif_file.has_alpha == heif_file[0].has_alpha
    assert heif_file.bit_depth == heif_file[0].bit_depth


def test_thumb_one_for_image():
    heif_file = open_heif(Path("images/pug_2_1.heic"))
    assert len([_ for _ in heif_file.thumbnails_all(one_for_image=True)]) == 1
    assert len([_ for _ in heif_file.thumbnails_all(one_for_image=False)]) == 1
    heif_file = open_heif(Path("images/pug_2_3.heic"))
    assert len([_ for _ in heif_file.thumbnails_all(one_for_image=True)]) == 2
    assert len([_ for _ in heif_file.thumbnails_all(one_for_image=False)]) == 3


def test_collect():
    heif_file = open_heif(Path("images/pug_2_1.heic"))
    second_heif = HeifFile({})
    second_heif.add_from_heif(heif_file)
    heif_file = second_heif
    collect()
    heif_file.load(everything=True)
    heif_file.unload(everything=True)
    collect()
    heif_file.load(everything=True)
    heif_file.close(only_fp=True)
    collect()
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


@pytest.mark.parametrize("img_path", minimal_dataset)
def test_inputs(img_path):
    with builtins.open(img_path, "rb") as f:
        b = f.read()
        non_exclusive = [open_heif(BytesIO(b)), open_heif(f)]
        exclusive = [open_heif(img_path), open_heif(b)]
        for heif_file in [*non_exclusive, *exclusive]:
            assert min(heif_file.size) > 0
            assert heif_file.info
            assert getattr(heif_file, "_heif_ctx") is not None
            collect()
            # This will load all data
            for image in heif_file:
                assert len(image.data) > 0
                for thumbnail in image.thumbnails:
                    assert len(thumbnail.data) > 0
            # Check if unloading data works. `unload` method is for private use, it must not be called in apps code.
            heif_file.unload(everything=True)
            collect()
            for image in heif_file:
                assert not getattr(image, "_img_data")
                for thumbnail in image.thumbnails:
                    assert not getattr(thumbnail, "_img_data")
            # After `unload` with if `fp` is present, it will read and load images again.
            for image in heif_file:
                assert len(image.data) > 0
                for thumbnail in image.thumbnails:
                    assert len(thumbnail.data) > 0
            heif_file.close(only_fp=True)
            collect()
            assert getattr(heif_file, "_heif_ctx") is not None
            # `fp` must be closed here.
            assert getattr(heif_file._heif_ctx, "fp") is None
            assert getattr(heif_file._heif_ctx, "_fp_close_after") == bool(heif_file in exclusive)
            # Create new heif_file
            second_heif = HeifFile({})
            second_heif.add_from_heif(heif_file)
            # This must do nothing, cause there is no `fp` in new heif file.
            second_heif.close(only_fp=True)
            collect()
            compare_heif_files_fields(second_heif, heif_file)
            heif_file.unload()
            collect()
            # After `unload` with `fp`=None, must be an exception accessing `data`
            with pytest.raises(HeifError):
                data = heif_file.data  # noqa
            heif_file.close()
            collect()
            # Closing original heif file, must not affect newly created.
            for image in second_heif:
                assert len(image.data) > 0
                for thumbnail in image.thumbnails:
                    assert len(thumbnail.data) > 0
            collect()
            # Create heif_file from already created and compare.
            heif_file = HeifFile({})
            heif_file.add_from_heif(second_heif)
            collect()
            compare_heif_files_fields(second_heif, heif_file)
            heif_file.close()
            second_heif.close()


@pytest.mark.parametrize("image_path", full_dataset)
def test_all(image_path):
    heif_file = open_heif(image_path)
    for c, image in enumerate(heif_file):
        image.misc["to_8bit"] = True
        pass_count = 2 if heif_file.bit_depth > 8 else 1
        for i in range(pass_count):
            if i == 1:
                image.misc["to_8bit"] = False
                image.unload()
            assert min(image.size) > 0
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
            assert image.color != HeifColorspace.UNDEFINED
            assert isinstance(image.load(), HeifImage)
    heif_file.close()
    assert getattr(heif_file, "_heif_ctx") is None
    collect()
    # Here will be no exception, heif_file is in `closed` state without `_heif_ctx` and will not try to load anything.
    assert heif_file.data is None
