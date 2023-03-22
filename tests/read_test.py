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


def test_open_heif():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    for im in heif_file:
        assert not im._data


def test_read_heif():
    heif_file = pillow_heif.read_heif(Path("images/heif/zPug_3.heic"))
    for im in heif_file:
        assert im._data


def test_bgr_mode_with_disabled_postprocess():
    with pytest.raises(ValueError):
        pillow_heif.open_heif(Path("images/heif/RGB_8__29x100.heif"), bgr_mode=True, postprocess=False)


def test_add_empty_from_pillow():
    im = Image.new(mode="L", size=(1, 0))
    heif = pillow_heif.HeifFile()
    with pytest.raises(ValueError):
        heif.add_from_pillow(im)


@pytest.mark.parametrize("img_path", dataset.CORRUPTED_DATASET)
def test_heif_corrupted_open(img_path):
    for input_type in [img_path.read_bytes(), BytesIO(img_path.read_bytes()), img_path, builtins.open(img_path, "rb")]:
        try:
            _ = pillow_heif.open_heif(input_type).data
            assert False
        except ValueError as exception:
            assert str(exception).find("Invalid input") != -1


@pytest.mark.parametrize("img_path", dataset.CORRUPTED_DATASET)
def test_pillow_corrupted_open(img_path):
    for input_type in [BytesIO(img_path.read_bytes()), img_path, builtins.open(img_path, "rb")]:
        with pytest.raises(UnidentifiedImageError):
            Image.open(input_type)


def test_heif_image_order():
    im = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    assert im.info["primary"] and im.primary_index == 1
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


@pytest.mark.parametrize("img_path", [Path("images/heif/RGBA_10__29x100.heif"), Path("images/heif/zPug_3.heic")])
def test_heif_inputs(img_path):
    with builtins.open(img_path, "rb") as fh:
        b = fh.read()
        bytes_io = BytesIO(b)
        for fp in [bytes_io, fh, img_path, img_path.as_posix(), b]:
            heif_file = pillow_heif.open_heif(fp)
            assert heif_file.mimetype
            assert min(heif_file.size) > 0
            assert heif_file.info
            assert getattr(heif_file[0], "_c_image") is not None
            collect()
            for image in heif_file:
                assert not getattr(image, "_data")
                assert len(image.data) > 0
                assert getattr(image, "_data")
            collect()
            for image in heif_file:
                assert len(image.data) > 0
            # Create new heif_file
            heif_file_from = pillow_heif.HeifFile()
            heif_file_from.add_from_heif(heif_file[0])
            collect()
            helpers.compare_heif_files_fields(heif_file_from[0], heif_file[0])
            heif_file = None  # noqa
            collect()
            assert len(heif_file_from[0].data)
            if not isinstance(fp, (Path, str, bytes)):
                assert not fp.closed


@pytest.mark.parametrize("img_path", [Path("images/heif/RGBA_10__29x100.heif"), Path("images/heif/zPug_3.heic")])
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
            helpers.compare_heif_to_pillow_fields(heif_image[0], pillow_image)
            assert len(pillow_heif.from_pillow(pillow_image)) == 1
            assert getattr(pillow_image, "fp") is None
            if not isinstance(fp, (Path, str)):
                assert not fp.closed


def test_pillow_after_load():
    img = Image.open(Path("images/heif/RGBA_10__29x100.heif"))
    assert getattr(img, "_heif_file") is not None
    for i in range(3):
        img.load()
        collect()
        assert not getattr(img, "is_animated")
        assert getattr(img, "n_frames") == 1
        assert not img.info["thumbnails"]
        assert getattr(img, "_heif_file") is None
        assert len(ImageSequence.Iterator(img)[0].tobytes())
    img = Image.open(Path("images/heif/zPug_3.heic"))
    for i in range(3):
        collect()
        assert getattr(img, "is_animated")
        assert getattr(img, "n_frames") == 3
        assert len(img.info["thumbnails"]) == 0 if i else 1
        assert getattr(img, "_heif_file") is not None
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
        heif_file_from = pillow_heif.HeifFile()
        for img in heif_file:
            heif_file_from.add_from_heif(img)
        collect()
        # Create Heif from created Heif
        heif_file_from_from = pillow_heif.HeifFile()
        for img in heif_file_from:
            heif_file_from_from.add_from_heif(img)
        collect()
        helpers.compare_heif_files_fields(heif_file, heif_file_from)
        # Closing original Heif must not affect data in others two
        heif_file = None  # noqa
        collect()
        helpers.compare_heif_files_fields(heif_file_from, heif_file_from_from)

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
    helpers.compare_heif_files_fields(heif_file, heif_from_pillow)


def test_heif_file_to_pillow():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    helpers.assert_image_equal(heif_file.to_pillow(), heif_file[1].to_pillow())


@pytest.mark.parametrize("image_path", dataset.FULL_DATASET)
def test_heif_read_images(image_path):
    def test_read_image(convert_hdr_to_8bit: bool) -> bool:
        heif_file = pillow_heif.open_heif(image_path, convert_hdr_to_8bit=convert_hdr_to_8bit)
        for image in heif_file:
            assert min(image.size) > 0
            assumed_mode = "RGBA" if image.has_alpha else "RGB"
            minimal_stride = image.size[0] * 4 if image.has_alpha else image.size[0] * 3
            if image.info["bit_depth"] > 8 and not convert_hdr_to_8bit:
                assumed_mode += ";16"
                minimal_stride *= 2
            assert image.mode == assumed_mode
            assert image.info["bit_depth"] >= 8
            assert image.stride >= minimal_stride
            assert len(image.data) == image.stride * image.size[1]
        return heif_file.info["bit_depth"] > 8

    one_more = test_read_image(False)
    if one_more:
        test_read_image(True)


@pytest.mark.parametrize("image_path", dataset.FULL_DATASET)
def test_pillow_read_images(image_path):
    pillow_image = Image.open(image_path)
    assert getattr(pillow_image, "fp") is not None
    assert getattr(pillow_image, "_heif_file") is not None
    pillow_image.verify()
    images_count = len(list(ImageSequence.Iterator(pillow_image)))
    for i, image in enumerate(ImageSequence.Iterator(pillow_image)):
        assert image.info
        assert image.custom_mimetype in ("image/heic", "image/heif", "image/heif-sequence", "image/avif")
        if "icc_profile" in image.info and len(image.info["icc_profile"]) > 0:
            ImageCms.getOpenProfile(BytesIO(pillow_image.info["icc_profile"]))
        collect()
        assert len(ImageSequence.Iterator(pillow_image)[i].tobytes())
        assert isinstance(image.getxmp(), dict)
    assert getattr(pillow_image, "fp") is None
    if images_count > 1:
        assert getattr(pillow_image, "_heif_file") is not None
    else:
        assert getattr(pillow_image, "_heif_file") is None
        # Testing here one more time, just for sure, that missing `heif_file` does not affect anything.
        collect()
        assert pillow_image.tobytes()
        assert len(ImageSequence.Iterator(pillow_image)[0].tobytes())


@pytest.mark.parametrize("img_path", dataset.TRUNCATED_DATASET)
def test_pillow_truncated_fail(img_path):
    truncated_heif = Image.open(img_path)
    with pytest.raises(EOFError):
        truncated_heif.load()


@mock.patch("PIL.ImageFile.LOAD_TRUNCATED_IMAGES", True)
@pytest.mark.parametrize("img_path", dataset.TRUNCATED_DATASET)
def test_pillow_truncated_ok(img_path):
    im = Image.open(img_path)
    im.load()


def test_heif_index():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    with pytest.raises(IndexError):
        _ = heif_file[-1].data
    with pytest.raises(IndexError):
        _ = heif_file[len(heif_file)].data
    with pytest.raises(IndexError):
        del heif_file[-1]
    with pytest.raises(IndexError):
        del heif_file[len(heif_file)]


def test_heif_etc():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    _ = heif_file.data
    assert getattr(heif_file[1], "_data")
    assert not getattr(heif_file[0], "_data")
    assert not getattr(heif_file[2], "_data")
    assert heif_file.size == heif_file[1].size
    assert heif_file.mode == heif_file[1].mode
    assert len(heif_file.data) == len(heif_file[1].data)
    assert heif_file.stride == heif_file[1].stride
    assert heif_file.has_alpha == heif_file[1].has_alpha
    assert heif_file.premultiplied_alpha == heif_file[1].premultiplied_alpha
    assert heif_file.info == heif_file[1].info


def test_heif_only_image_reference():
    empty_heif_container = pillow_heif.HeifFile()
    empty_heif_container.add_from_heif(pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))[0])
    empty_heif_container.add_from_heif(pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))[2])
    assert len(empty_heif_container) == 2
    assert empty_heif_container[0].data
    assert empty_heif_container[1].data


@pytest.mark.parametrize(
    "im_path,original_path",
    (
        ("images/heif/L_8__29x100.heif", "images/non_heif/L_8__29x100.png"),
        ("images/heif/L_8__128x128.heif", "images/non_heif/L_8__128x128.png"),
        ("images/heif/L_10__29x100.heif", "images/non_heif/L_16__29x100.png"),
        ("images/heif/L_10__128x128.heif", "images/non_heif/L_16__128x128.png"),
        ("images/heif/L_12__29x100.heif", "images/non_heif/L_16__29x100.png"),
        ("images/heif/L_12__128x128.heif", "images/non_heif/L_16__128x128.png"),
        ("images/heif/LA_8__29x100.heif", "images/non_heif/LA_8__29x100.png"),
        ("images/heif/LA_8__128x128.heif", "images/non_heif/LA_8__128x128.png"),
        ("images/heif/RGB_8__29x100.heif", "images/non_heif/RGB_8__29x100.png"),
        ("images/heif/RGB_8__128x128.heif", "images/non_heif/RGB_8__128x128.png"),
        ("images/heif/RGBA_8__29x100.heif", "images/non_heif/RGBA_8__29x100.png"),
        ("images/heif/RGBA_8__128x128.heif", "images/non_heif/RGBA_8__128x128.png"),
        ("images/heif/RGB_10__29x100.heif", "images/non_heif/RGB_16__29x100.png"),
        ("images/heif/RGB_10__128x128.heif", "images/non_heif/RGB_16__128x128.png"),
        ("images/heif/RGB_12__29x100.heif", "images/non_heif/RGB_16__29x100.png"),
        ("images/heif/RGB_12__128x128.heif", "images/non_heif/RGB_16__128x128.png"),
        ("images/heif/RGBA_10__29x100.heif", "images/non_heif/RGBA_16__29x100.png"),
        ("images/heif/RGBA_10__128x128.heif", "images/non_heif/RGBA_16__128x128.png"),
        ("images/heif/RGBA_12__29x100.heif", "images/non_heif/RGBA_16__29x100.png"),
        ("images/heif/RGBA_12__128x128.heif", "images/non_heif/RGBA_16__128x128.png"),
    ),
)
def test_hdr_read(im_path, original_path):
    helpers.compare_hashes([im_path, original_path], hash_size=16)


@pytest.mark.parametrize(
    "im_path,original_path",
    (
        ("images/heif/L_8__29x100.avif", "images/non_heif/L_8__29x100.png"),
        ("images/heif/L_8__128x128.avif", "images/non_heif/L_8__128x128.png"),
        ("images/heif/L_10__29x100.avif", "images/non_heif/L_16__29x100.png"),
        ("images/heif/L_10__128x128.avif", "images/non_heif/L_16__128x128.png"),
        ("images/heif/L_12__29x100.avif", "images/non_heif/L_16__29x100.png"),
        ("images/heif/L_12__128x128.avif", "images/non_heif/L_16__128x128.png"),
        ("images/heif/LA_8__29x100.avif", "images/non_heif/LA_8__29x100.png"),
        ("images/heif/LA_8__128x128.avif", "images/non_heif/LA_8__128x128.png"),
        ("images/heif/RGB_8__29x100.avif", "images/non_heif/RGB_8__29x100.png"),
        ("images/heif/RGB_8__128x128.avif", "images/non_heif/RGB_8__128x128.png"),
        ("images/heif/RGBA_8__29x100.avif", "images/non_heif/RGBA_8__29x100.png"),
        ("images/heif/RGBA_8__128x128.avif", "images/non_heif/RGBA_8__128x128.png"),
        ("images/heif/RGB_10__29x100.avif", "images/non_heif/RGB_16__29x100.png"),
        ("images/heif/RGB_10__128x128.avif", "images/non_heif/RGB_16__128x128.png"),
        ("images/heif/RGB_12__29x100.avif", "images/non_heif/RGB_16__29x100.png"),
        ("images/heif/RGB_12__128x128.avif", "images/non_heif/RGB_16__128x128.png"),
        ("images/heif/RGBA_10__29x100.avif", "images/non_heif/RGBA_16__29x100.png"),
        ("images/heif/RGBA_10__128x128.avif", "images/non_heif/RGBA_16__128x128.png"),
        ("images/heif/RGBA_12__29x100.avif", "images/non_heif/RGBA_16__29x100.png"),
        ("images/heif/RGBA_12__128x128.avif", "images/non_heif/RGBA_16__128x128.png"),
    ),
)
@pytest.mark.skipif(not helpers.aom(), reason="requires AVIF support.")
def test_hdr_read_avif(im_path, original_path):
    helpers.compare_hashes([im_path, original_path], hash_size=16)


@pytest.mark.parametrize(
    "image_path",
    (
        "images/heif_special/L_8__29(255)x100.heif",
        "images/heif_special/L_8__29x100(255).heif",
        "images/heif_special/L_8__29x100(100x29).heif",
    ),
)
def test_invalid_ispe_fail(image_path):
    im = Image.open(image_path)
    with pytest.raises(ValueError):
        im.load()


@pytest.mark.parametrize(
    "image_path",
    ("images/heif_special/L_8__128(64)x128(64).heif",),
)
def test_invalid_ispe_ok(image_path):
    im = Image.open(image_path)
    im.load()


@pytest.mark.parametrize(
    "image_path",
    (
        "images/heif_special/L_8__29(255)x100.heif",
        "images/heif_special/L_8__29x100(255).heif",
        "images/heif_special/L_8__128(64)x128(64).heif",
        "images/heif_special/L_8__29x100(100x29).heif",
    ),
)
@mock.patch("pillow_heif.options.ALLOW_INCORRECT_HEADERS", True)
def test_invalid_ispe_allow(image_path):
    im = Image.open(image_path)
    im.load()


@pytest.mark.parametrize(
    "image_path",
    (
        "images/heif_special/L_8__29(255)x100.heif",
        "images/heif_special/L_8__29x100(255).heif",
        "images/heif_special/L_8__128(64)x128(64).heif",
        "images/heif_special/L_8__29x100(100x29).heif",
    ),
)
@mock.patch("pillow_heif.options.ALLOW_INCORRECT_HEADERS", True)
def test_invalid_ispe_stride(image_path):
    im = pillow_heif.open_heif(image_path)
    stride = im.stride
    _ = im.data
    assert stride == im.stride
