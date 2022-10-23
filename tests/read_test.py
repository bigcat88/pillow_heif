import builtins
import os
from gc import collect
from io import BytesIO
from pathlib import Path
from unittest import mock

import dataset
import helpers
import pytest
from PIL import Image, ImageCms, ImageSequence, UnidentifiedImageError

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pillow_heif.register_avif_opener()
pillow_heif.register_heif_opener()


@pytest.mark.parametrize("img_path", dataset.CORRUPTED_DATASET)
def test_heif_corrupted_open(img_path):
    for input_type in [img_path.read_bytes(), BytesIO(img_path.read_bytes()), img_path, builtins.open(img_path, "rb")]:
        try:
            pillow_heif.open_heif(input_type).load()
            assert False
        except pillow_heif.HeifError as exception:
            assert exception.code == pillow_heif.HeifErrorCode.INVALID_INPUT
            assert repr(exception).find("HeifErrorCode.INVALID_INPUT") != -1
            assert str(exception).find("Invalid input") != -1


@pytest.mark.parametrize("img_path", dataset.CORRUPTED_DATASET)
def test_pillow_corrupted_open(img_path):
    for input_type in [BytesIO(img_path.read_bytes()), img_path, builtins.open(img_path, "rb")]:
        with pytest.raises(UnidentifiedImageError):
            Image.open(input_type)


def test_heif_image_order():
    im = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    assert im.info["primary"] and im.primary_index() == 1
    assert not im[0].info["primary"]
    assert im[1].info["primary"]
    assert not im[2].info["primary"]


def test_pillow_image_order():
    im = Image.open(Path("images/heif/zPug_3.heic"))
    assert im.info["primary"] and im.tell() == 1
    im.seek(0)
    assert not im.info["primary"]
    im.seek(1)
    assert im.info["primary"]
    im.seek(2)
    assert not im.info["primary"]


@pytest.mark.parametrize("img_path", [Path("images/heif/RGBA_10.heif"), Path("images/heif/zPug_3.heic")])
def test_heif_inputs(img_path):
    def perform_test_input():
        with builtins.open(img_path, "rb") as fh:
            b = fh.read()
            bytes_io = BytesIO(b)
            for fp in [bytes_io, fh, img_path, img_path.as_posix(), b]:
                heif_file = pillow_heif.open_heif(fp)
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
                if not pillow_heif.options().ctx_in_memory:
                    assert getattr(heif_file[0]._heif_ctx, "fp") is not None
                    assert getattr(heif_file[0]._heif_ctx, "_fp_close_after") == isinstance(fp, (Path, str, bytes))
                # Create new heif_file
                heif_file_from = pillow_heif.HeifFile().add_from_heif(heif_file)
                collect()
                helpers.compare_heif_files_fields(heif_file_from, heif_file, ignore=["original_bit_depth"])
                for _ in heif_file:
                    _.unload()
                for _ in heif_file_from:
                    _.unload()
                collect()
                helpers.compare_heif_files_fields(heif_file_from, heif_file, ignore=["original_bit_depth"])
                heif_file = None  # noqa
                assert len(heif_file_from[len(heif_file_from) - 1].data)
                if not isinstance(fp, (Path, str, bytes)):
                    assert not fp.closed

    perform_test_input()
    try:
        pillow_heif.options().ctx_in_memory = False
        perform_test_input()
    finally:
        pillow_heif.options().ctx_in_memory = True


@pytest.mark.parametrize("img_path", [Path("images/heif/RGBA_10.heif"), Path("images/heif/zPug_3.heic")])
def test_pillow_inputs(img_path):
    with builtins.open(img_path, "rb") as fh:
        bytes_io = BytesIO(fh.read())
        for fp in [bytes_io, fh, img_path, img_path.as_posix()]:
            pillow_image = Image.open(fp)
            assert getattr(pillow_image, "fp") is not None
            pillow_image.load()
            for frame in ImageSequence.Iterator(pillow_image):
                assert len(frame.tobytes()) > 0
            heif_image = pillow_heif.from_pillow(pillow_image)
            helpers.compare_heif_to_pillow_fields(heif_image, pillow_image)
            assert len(pillow_heif.from_pillow(pillow_image, load_one=True)) == 1
            if getattr(pillow_image, "n_frames") > 1:
                assert getattr(pillow_image, "fp") is not None
            else:
                assert getattr(pillow_image, "fp") is None
            if not isinstance(fp, (Path, str)):
                assert not fp.closed


def test_pillow_after_load():
    img = Image.open(Path("images/heif/RGBA_10.heif"))
    assert getattr(img, "heif_file") is not None
    for i in range(3):
        img.load()
        collect()
        assert not getattr(img, "is_animated")
        assert getattr(img, "n_frames") == 1
        assert not img.info["thumbnails"]
        assert getattr(img, "heif_file") is None
        assert len(ImageSequence.Iterator(img)[0].tobytes())
    img = Image.open(Path("images/heif/zPug_3.heic"))
    for i in range(3):
        collect()
        assert getattr(img, "is_animated")
        assert getattr(img, "n_frames") == 3
        assert len(img.info["thumbnails"]) == 0 if i else 1
        assert getattr(img, "heif_file") is not None
        assert len(ImageSequence.Iterator(img)[0].info["thumbnails"]) == 2
        assert len(ImageSequence.Iterator(img)[1].info["thumbnails"]) == 1
        assert len(ImageSequence.Iterator(img)[2].info["thumbnails"]) == 0
        assert len(ImageSequence.Iterator(img)[0].tobytes())
        assert len(ImageSequence.Iterator(img)[1].tobytes())
        assert len(ImageSequence.Iterator(img)[2].tobytes())


@pytest.mark.parametrize("img_path", dataset.MINIMAL_DATASET)
def test_heif_from_heif(img_path):
    def heif_from_heif(hdr_to_8bit=True):
        heif_file = pillow_heif.open_heif(img_path, convert_hdr_to_8bit=hdr_to_8bit)
        collect()
        # Create Heif from Heif
        heif_file_from = pillow_heif.HeifFile().add_from_heif(heif_file)
        collect()
        # Create Heif from created Heif
        heif_file_from_from = pillow_heif.HeifFile().add_from_heif(heif_file_from)
        for _ in heif_file:
            _.unload()
        collect()
        helpers.compare_heif_files_fields(heif_file, heif_file_from, ignore=["original_bit_depth"])
        # Closing original Heif must not affect data in others two
        heif_file = None  # noqa
        for _ in heif_file_from:
            _.unload()
        for _ in heif_file_from_from:
            _.unload()
        collect()
        heif_file_from.load(everything=True)
        heif_file_from_from.load(everything=True)
        helpers.compare_heif_files_fields(heif_file_from, heif_file_from_from, ignore=["original_bit_depth"])
        heif_file_from = None  # noqa
        assert len(heif_file_from_from[len(heif_file_from_from) - 1].data)

    heif_from_heif(hdr_to_8bit=True)
    heif_from_heif(hdr_to_8bit=False)


@pytest.mark.parametrize("image_path", dataset.MINIMAL_DATASET)
def test_to_from_pillow(image_path):
    heif_file = pillow_heif.open_heif(image_path)
    images_list = [i.to_pillow() for i in heif_file]
    for i, image in enumerate(heif_file):
        helpers.compare_heif_to_pillow_fields(image, images_list[i])
    heif_from_pillow = pillow_heif.HeifFile()
    for image in images_list:
        heif_from_pillow.add_from_pillow(image)
    helpers.compare_heif_files_fields(heif_file, heif_from_pillow, ignore=["original_bit_depth"])


def test_heif_file_to_pillow():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    helpers.assert_image_equal(heif_file.to_pillow(), heif_file[1].to_pillow())


@pytest.mark.parametrize("image_path", dataset.FULL_DATASET)
def test_heif_read_images(image_path):
    def test_read_image(convert_hdr_to_8bit: bool) -> bool:
        heif_file = pillow_heif.open_heif(image_path, convert_hdr_to_8bit=convert_hdr_to_8bit)
        for image in heif_file:
            assert isinstance(pillow_heif.getxmp(image.info["xmp"]), dict)
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
            assert isinstance(image.load(), pillow_heif.HeifImage)
            for thumbnail in image.thumbnails:
                minimal_stride = thumbnail.size[0] * 4 if thumbnail.has_alpha else thumbnail.size[0] * 3
                if thumbnail.bit_depth > 8:
                    minimal_stride *= 2
                assert thumbnail.stride >= minimal_stride
                assert len(thumbnail.data) == thumbnail.stride * thumbnail.size[1]
                assert isinstance(thumbnail.load(), pillow_heif.HeifThumbnail)
        return heif_file.bit_depth > 8

    one_more = test_read_image(False)
    if one_more:
        test_read_image(True)
    try:
        pillow_heif.options().ctx_in_memory = False
        one_more = test_read_image(False)
        if one_more:
            test_read_image(True)
    finally:
        pillow_heif.options().ctx_in_memory = True


@pytest.mark.parametrize("image_path", dataset.FULL_DATASET)
def test_pillow_read_images(image_path):
    def test_read_image():
        pillow_image = Image.open(image_path)
        assert getattr(pillow_image, "fp") is not None
        assert getattr(pillow_image, "heif_file") is not None
        assert not getattr(pillow_image, "_close_exclusive_fp_after_loading")
        pillow_image.verify()
        images_count = len([_ for _ in ImageSequence.Iterator(pillow_image)])
        for i, image in enumerate(ImageSequence.Iterator(pillow_image)):
            assert image.info
            assert image.custom_mimetype in ("image/heic", "image/heif", "image/heif-sequence", "image/avif")
            if "icc_profile" in image.info and len(image.info["icc_profile"]) > 0:
                ImageCms.getOpenProfile(BytesIO(pillow_image.info["icc_profile"]))
            collect()
            assert len(ImageSequence.Iterator(pillow_image)[i].tobytes())
            for thumb in ImageSequence.Iterator(pillow_image)[i].info["thumbnails"]:
                if images_count > 1:
                    assert thumb.data is not None
                else:
                    assert thumb.data is None
            assert isinstance(image.getxmp(), dict)
        if images_count > 1:
            assert getattr(pillow_image, "fp") is not None
            assert getattr(pillow_image, "heif_file") is not None
            assert not getattr(pillow_image, "_close_exclusive_fp_after_loading")
        else:
            assert getattr(pillow_image, "fp") is None
            assert getattr(pillow_image, "heif_file") is None
            assert getattr(pillow_image, "_close_exclusive_fp_after_loading")
            # Testing here one more time, just for sure, that missing `heif_file` not affect anything.
            collect()
            assert pillow_image.tobytes()
            assert len(ImageSequence.Iterator(pillow_image)[0].tobytes())

    test_read_image()
    try:
        pillow_heif.options().ctx_in_memory = False
        test_read_image()
    finally:
        pillow_heif.options().ctx_in_memory = True


@pytest.mark.parametrize("img_path", dataset.TRUNCATED_DATASET)
def test_pillow_truncated_fail(img_path):
    truncated_heif = Image.open(img_path)
    with pytest.raises(pillow_heif.HeifError):
        truncated_heif.load()


@mock.patch("PIL.ImageFile.LOAD_TRUNCATED_IMAGES", True)
@pytest.mark.parametrize("img_path", dataset.TRUNCATED_DATASET)
def test_pillow_truncated_ok(img_path):
    im = Image.open(img_path)
    im.load()


def test_heif_index():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
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


@mock.patch("pillow_heif.misc.ElementTree", None)
def test_no_defusedxml(monkeypatch):
    with pytest.warns(UserWarning):
        pillow_heif.getxmp(b"xmp_data")


def test_read_heif():
    heif_file = pillow_heif.read_heif(Path("images/heif/zPug_3.heic"))
    for im in heif_file:
        assert im._img_data
        for thumbnail in im.thumbnails:
            assert not thumbnail._img_data
            thumbnail.load()
            assert thumbnail._img_data


def test_heif_etc():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    heif_file.load(everything=False)
    assert getattr(heif_file[1], "_img_data")
    assert not getattr(heif_file[0], "_img_data")
    assert not getattr(heif_file[2], "_img_data")
    assert heif_file.size == heif_file[1].size
    assert heif_file.mode == heif_file[1].mode
    assert len(heif_file.data) == len(heif_file[1].data)
    assert heif_file.stride == heif_file[1].stride
    assert heif_file.has_alpha == heif_file[1].has_alpha
    assert heif_file.premultiplied_alpha == heif_file[1].premultiplied_alpha
    assert heif_file.bit_depth == heif_file[1].bit_depth
    assert heif_file.original_bit_depth == heif_file[1].original_bit_depth


def test_heif_only_image_reference():
    empty_heif_container = pillow_heif.HeifFile()
    empty_heif_container.add_from_heif(pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))[0])
    empty_heif_container.add_from_heif(pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))[2])
    assert len(empty_heif_container) == 2
    empty_heif_container.load(everything=True)


@pytest.mark.parametrize(
    "im_path,original_path",
    (
        ("images/heif/L_10.heif", "images/non_heif/L_16.png"),
        ("images/heif/L_12.heif", "images/non_heif/L_16.png"),
        ("images/heif/RGB_10.heif", "images/non_heif/RGB_16.png"),
        ("images/heif/RGB_12.heif", "images/non_heif/RGB_16.png"),
        ("images/heif/RGBA_10.heif", "images/non_heif/RGBA_16.png"),
        ("images/heif/RGBA_12.heif", "images/non_heif/RGBA_16.png"),
    ),
)
def test_hdr_read(im_path, original_path):
    helpers.compare_hashes([im_path, original_path], max_difference=1)


@pytest.mark.parametrize(
    "im_path,original_path",
    (
        ("images/heif/L_10.avif", "images/non_heif/L_16.png"),
        ("images/heif/L_12.avif", "images/non_heif/L_16.png"),
        ("images/heif/RGB_10.avif", "images/non_heif/RGB_16.png"),
        ("images/heif/RGB_12.avif", "images/non_heif/RGB_16.png"),
        ("images/heif/RGBA_10.avif", "images/non_heif/RGBA_16.png"),
        ("images/heif/RGBA_12.avif", "images/non_heif/RGBA_16.png"),
    ),
)
@pytest.mark.skipif(not helpers.aom_dec(), reason="requires AVIF decoder.")
def test_hdr_read_avif(im_path, original_path):
    helpers.compare_hashes([im_path, original_path], max_difference=1)
