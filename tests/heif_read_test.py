import builtins
import os
from gc import collect
from io import BytesIO
from pathlib import Path

import dataset
import pytest
from helpers import compare_heif_files_fields

from pillow_heif import (
    HeifError,
    HeifErrorCode,
    HeifFile,
    HeifImage,
    HeifThumbnail,
    getxmp,
    open_heif,
    options,
    read_heif,
    register_heif_opener,
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


@pytest.mark.parametrize("img_path", dataset.CORRUPTED_DATASET)
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
    heif_file = open_heif(Path("images/rgb8_150_128_2_1.heic"))
    with pytest.raises(IndexError):
        heif_file[-1].load()
    with pytest.raises(IndexError):
        heif_file[len(heif_file)].load()
    with pytest.raises(IndexError):
        heif_file[0].thumbnails[len(heif_file[0].thumbnails)].load()
    with pytest.raises(IndexError):
        del heif_file[-1]
    with pytest.raises(IndexError):
        del heif_file[len(heif_file)]


def test_etc():
    heif_file = open_heif(Path("images/rgb8_128_128_2_1.heic"))
    heif_file.load(everything=False)
    assert getattr(heif_file[0], "_img_data")
    assert not getattr(heif_file[1], "_img_data")
    assert heif_file.size == heif_file[0].size
    assert heif_file.mode == heif_file[0].mode
    assert len(heif_file.data) == len(heif_file[0].data)
    assert heif_file.stride == heif_file[0].stride
    assert heif_file.has_alpha == heif_file[0].has_alpha
    assert heif_file.bit_depth == heif_file[0].bit_depth


@pytest.mark.parametrize("img_path", dataset.MINIMAL_DATASET)
def test_heif_from_heif(img_path):
    def heif_from_heif(hdr_to_8bit=True):
        heif_file = open_heif(img_path, convert_hdr_to_8bit=hdr_to_8bit)
        collect()
        # Create Heif from Heif
        heif_file_from = HeifFile().add_from_heif(heif_file)
        collect()
        # Create Heif from created Heif
        heif_file_from_from = HeifFile().add_from_heif(heif_file_from)
        for _ in heif_file:
            _.unload()
        collect()
        compare_heif_files_fields(heif_file, heif_file_from, ignore=["original_bit_depth"])
        # Closing original Heif must not affect data in others two
        heif_file = None  # noqa
        for _ in heif_file_from:
            _.unload()
        for _ in heif_file_from_from:
            _.unload()
        collect()
        heif_file_from.load(everything=True)
        heif_file_from_from.load(everything=True)
        compare_heif_files_fields(heif_file_from, heif_file_from_from, ignore=["original_bit_depth"])
        heif_file_from = None  # noqa
        assert len(heif_file_from_from[len(heif_file_from_from) - 1].data)

    heif_from_heif(hdr_to_8bit=True)
    heif_from_heif(hdr_to_8bit=False)


@pytest.mark.parametrize("img_path", dataset.MINIMAL_DATASET)
def test_inputs(img_path):
    def perform_test_input():
        with builtins.open(img_path, "rb") as fh:
            b = fh.read()
            bytes_io = BytesIO(b)
            for fp in [bytes_io, fh, img_path, img_path.as_posix(), b]:
                heif_file = open_heif(fp)
                assert heif_file.mimetype
                assert min(heif_file.size) > 0
                assert heif_file.info
                assert getattr(heif_file[0], "_heif_ctx") is not None
                collect()
                # This will load all data
                for image in heif_file:
                    assert not getattr(image, "_img_data")
                    assert len(image.data) > 0
                    for thumbnail in image.thumbnails:
                        assert not getattr(thumbnail, "_img_data")
                        assert len(thumbnail.data) > 0
                        thumbnail.unload()
                    image.unload()
                collect()
                for image in heif_file:
                    assert not getattr(image, "_img_data")
                    assert len(image.data) > 0
                    for thumbnail in image.thumbnails:
                        assert not getattr(thumbnail, "_img_data")
                        assert len(thumbnail.data) > 0
                collect()
                assert getattr(heif_file[0], "_heif_ctx") is not None
                if not options().ctx_in_memory:
                    assert getattr(heif_file[0]._heif_ctx, "fp") is not None
                    assert getattr(heif_file[0]._heif_ctx, "_fp_close_after") == isinstance(fp, (Path, str, bytes))
                # Create new heif_file
                heif_file_from = HeifFile().add_from_heif(heif_file)
                collect()
                compare_heif_files_fields(heif_file_from, heif_file, ignore=["original_bit_depth"])
                for _ in heif_file:
                    _.unload()
                for _ in heif_file_from:
                    _.unload()
                collect()
                compare_heif_files_fields(heif_file_from, heif_file, ignore=["original_bit_depth"])
                heif_file = None  # noqa
                assert len(heif_file_from[len(heif_file_from) - 1].data)
                if not isinstance(fp, (Path, str, bytes)):
                    assert not fp.closed

    perform_test_input()
    try:
        options().ctx_in_memory = False
        perform_test_input()
    finally:
        options().ctx_in_memory = True


def test_only_heif_image_reference():
    empty_heif_container = HeifFile()
    empty_heif_container.add_from_heif(open_heif(Path("images/rgb8_512_512_1_0.heic"))[0])
    empty_heif_container.add_from_heif(open_heif(Path("images/rgb8_128_128_2_1.heic"))[1])
    assert len(empty_heif_container) == 2
    empty_heif_container.load(everything=True)


@pytest.mark.parametrize("image_path", dataset.FULL_DATASET)
def test_all(image_path):
    def perform_test_all(convert_hdr_to_8bit: bool) -> bool:
        heif_file = open_heif(image_path, convert_hdr_to_8bit=convert_hdr_to_8bit)
        for image in heif_file:
            assert isinstance(getxmp(image.info["xmp"]), dict)
            assert min(image.size) > 0
            assumed_mode = "RGBA" if image.has_alpha else "RGB"
            if image.bit_depth > 8:
                assumed_mode += f";{image.bit_depth}"
            assert image.mode == assumed_mode
            assert image.bit_depth >= 8
            minimal_stride = image.size[0] * 4 if image.has_alpha else image.size[0] * 3
            if image.bit_depth > 8:
                minimal_stride *= 2
            assert image.stride >= minimal_stride
            assert len(image.data) == image.stride * image.size[1]
            # This will load thumbnails too
            assert isinstance(image.load(), HeifImage)
            for thumbnail in image.thumbnails:
                minimal_stride = thumbnail.size[0] * 4 if thumbnail.has_alpha else thumbnail.size[0] * 3
                if thumbnail.bit_depth > 8:
                    minimal_stride *= 2
                assert thumbnail.stride >= minimal_stride
                assert len(thumbnail.data) == thumbnail.stride * thumbnail.size[1]
                assert isinstance(thumbnail.load(), HeifThumbnail)
        return heif_file.bit_depth > 8

    one_more = perform_test_all(False)
    if one_more:
        perform_test_all(True)
    try:
        options().ctx_in_memory = False
        one_more = perform_test_all(False)
        if one_more:
            perform_test_all(True)
    finally:
        options().ctx_in_memory = True


def test_no_defusedxml(monkeypatch):
    import pillow_heif

    with monkeypatch.context() as m:
        m.setattr(pillow_heif.misc, "ElementTree", None)
        heif_file = open_heif(Path("images/rgb8_512_512_1_0.heic"))
        with pytest.warns(UserWarning):
            getxmp(heif_file.info["xmp"])


def test_read_heif():
    heif_file = read_heif(Path("images/rgb8_210_128_2_2.heic"))
    for img in heif_file:
        assert img._img_data
        for thumbnail in img.thumbnails:
            assert not thumbnail._img_data
            thumbnail.load()
            assert thumbnail._img_data
