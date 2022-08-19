from io import BytesIO
from os import getenv
from pathlib import Path
from typing import Union

from PIL import Image, ImageMath, ImageOps

from pillow_heif import (
    HeifCompressionFormat,
    HeifFile,
    HeifImage,
    HeifThumbnail,
    add_thumbnails,
    have_decoder_for_format,
    have_encoder_for_format,
    libheif_info,
)

try:
    import numpy as np
except ImportError:
    np = None


RELEASE_FULL_FLAG = getenv("PH_FULL_ACTION", "0") == "1"
RELEASE_LIGHT_FLAG = getenv("PH_LIGHT_ACTION", "0") == "1"


def assert_image_equal(a, b):
    assert a.mode == b.mode
    assert a.size == b.size
    assert a.tobytes() == b.tobytes()


def convert_to_comparable(a, b):
    new_a, new_b = a, b
    if a.mode == "P":
        new_a = Image.new("L", a.size)
        new_b = Image.new("L", b.size)
        new_a.putdata(a.getdata())
        new_b.putdata(b.getdata())
    elif a.mode == "I;16":
        new_a = a.convert("I")
        new_b = b.convert("I")
    return new_a, new_b


def assert_image_similar(a, b, epsilon=0.0):
    assert a.mode == b.mode
    assert a.size == b.size
    a, b = convert_to_comparable(a, b)
    diff = 0
    for ach, bch in zip(a.split(), b.split()):
        ch_diff = ImageMath.eval("abs(a - b)", a=ach, b=bch).convert("L")
        diff += sum(i * num for i, num in enumerate(ch_diff.histogram()))
    ave_diff = diff / (a.size[0] * a.size[1])
    assert epsilon >= ave_diff


def compare_hashes(pillow_images: list, hash_size=16, max_difference=0):
    if np is None:
        return
    image_hashes = []
    for pillow_image in pillow_images:
        if isinstance(pillow_image, (str, Path, BytesIO)):
            pillow_image = Image.open(pillow_image)
        pillow_image = ImageOps.exif_transpose(pillow_image)
        pillow_image = pillow_image.convert("L").resize((hash_size + 1, hash_size), Image.ANTIALIAS)
        pixels = np.asarray(pillow_image)  # noqa
        diff = pixels[:, 1:] > pixels[:, :-1]
        image_hash = diff.flatten()  # noqa
        for _ in range(len(image_hashes)):
            distance = np.count_nonzero(image_hash != image_hashes[_])
            assert distance <= max_difference, f"{distance} > {max_difference}"
        image_hashes.append(image_hash)


def compare_heif_files_fields(
    heif1: Union[HeifFile, HeifImage], heif2: Union[HeifFile, HeifImage], ignore=None, thumb_size_max_differ=2
):
    def compare_images_fields(image1: HeifImage, image2: HeifImage):
        assert image1.size == image2.size
        assert image1.mode == image2.mode
        if "original_bit_depth" not in ignore:
            assert image1.original_bit_depth == image2.original_bit_depth
        assert image1.bit_depth == image2.bit_depth
        if "stride" not in ignore:
            assert image1.stride == image2.stride
            assert len(image1.data) == len(image2.data)
        for i_thumb, thumbnail in enumerate(image1.thumbnails):
            with_difference = thumbnail.size[0] - image2.thumbnails[i_thumb].size[0]
            height_difference = thumbnail.size[1] - image2.thumbnails[i_thumb].size[1]
            assert with_difference + height_difference <= thumb_size_max_differ
            assert thumbnail.mode == image2.thumbnails[i_thumb].mode
            if "original_bit_depth" not in ignore:
                assert thumbnail.original_bit_depth == image2.thumbnails[i_thumb].original_bit_depth
            assert thumbnail.bit_depth == image2.thumbnails[i_thumb].bit_depth
        assert image1.info["exif"] == image2.info["exif"]
        assert image1.info["xmp"] == image2.info["xmp"]
        for block_i, block in enumerate(image1.info["metadata"]):
            assert block["data"] == image1.info["metadata"][block_i]["data"]
            assert block["content_type"] == image1.info["metadata"][block_i]["content_type"]
            assert block["type"] == image1.info["metadata"][block_i]["type"]

    if ignore is None:
        ignore = []
    if isinstance(heif1, HeifFile):
        for i, image in enumerate(heif1):
            compare_images_fields(image, heif2[i])
    else:
        compare_images_fields(heif1, heif2)


def compare_heif_to_pillow_fields(heif: Union[HeifFile, HeifImage, HeifThumbnail], pillow: Image):
    def compare_images_fields(heif_image: Union[HeifImage, HeifThumbnail], pillow_image: Image):
        assert heif_image.size == pillow_image.size
        assert heif_image.mode == pillow_image.mode
        for k in ("exif", "xmp", "metadata"):
            if heif_image.info.get(k, None):
                if isinstance(heif_image.info[k], (bool, int, float, str)):
                    assert heif_image.info[k] == pillow_image.info[k]
                else:
                    assert len(heif_image.info[k]) == len(pillow_image.info[k])
        for k in ("icc_profile", "icc_profile_type", "nclx_profile"):
            if heif_image.info.get(k, None):
                assert len(heif_image.info[k]) == len(pillow_image.info[k])

    if isinstance(heif, HeifFile):
        for i, image in enumerate(heif):
            pillow.seek(i)
            compare_images_fields(image, pillow)
    else:
        compare_images_fields(heif, pillow)


def create_heif(size: tuple = None, thumb_boxes: list = None, n_images=1, **kwargs) -> BytesIO:
    if size is None:
        size = (512, 512)
    if thumb_boxes is None:
        thumb_boxes = []
    im_heif = HeifFile()
    for i in range(n_images):
        im_heif.add_from_pillow(Image.effect_mandelbrot(size, (-3, -2.5, 2, 2.5), 100))
        size = (int(size[0] / 2), int(size[1] / 2))
        add_thumbnails(im_heif[i], thumb_boxes)
    heif_buf = BytesIO()
    im_heif.save(heif_buf, **kwargs)
    return heif_buf


def gradient_rgb():
    return Image.merge(
        "RGB",
        [
            Image.linear_gradient(mode="L"),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_90),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_180),
        ],
    )


def gradient_rgb_bytes(im_format: str) -> bytearray:
    _ = BytesIO()
    gradient_rgb().save(_, format=im_format)
    return bytearray(_.getbuffer().tobytes())


def gradient_rgba():
    return Image.merge(
        "RGBA",
        [
            Image.linear_gradient(mode="L"),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_90),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_180),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_270),
        ],
    )


def gradient_rgba_bytes(im_format: str) -> bytearray:
    _ = BytesIO()
    gradient_rgba().save(_, format=im_format)
    return bytearray(_.getbuffer().tobytes())


def gradient_la():
    return Image.merge(
        "LA",
        [
            Image.linear_gradient(mode="L"),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_90),
        ],
    )


def gradient_la_bytes(im_format: str) -> bytearray:
    _ = BytesIO()
    gradient_la().save(_, format=im_format)
    return bytearray(_.getbuffer().tobytes())


def gradient_p_bytes(im_format: str) -> bytearray:
    _ = BytesIO()
    im = Image.linear_gradient(mode="L")
    im = im.convert(mode="P")
    im.save(_, format=im_format)
    return bytearray(_.getbuffer().tobytes())


def gradient_pa():
    return Image.merge(
        "PA",
        [
            Image.linear_gradient(mode="L"),
            Image.linear_gradient(mode="L").transpose(Image.ROTATE_90),
        ],
    )


def gradient_pa_bytes(im_format: str) -> bytearray:
    _ = BytesIO()
    gradient_la().save(_, format=im_format)
    return bytearray(_.getbuffer().tobytes())


def hevc_enc() -> bool:
    if getenv("PH_TESTS_NO_HEVC_ENC", "0") != "0":
        return False
    return have_encoder_for_format(HeifCompressionFormat.HEVC)


def aom_dec() -> bool:
    if getenv("PH_TESTS_NO_AVIF_DEC", "0") != "0":
        return False
    if libheif_info()["version"]["aom"] == "Rav1e encoder":
        return False
    return have_decoder_for_format(HeifCompressionFormat.AV1)


def aom_enc() -> bool:
    if getenv("PH_TESTS_NO_AVIF_ENC", "0") != "0":
        return False
    if libheif_info()["version"]["aom"] == "Rav1e encoder":
        return False
    return have_encoder_for_format(HeifCompressionFormat.AV1)
