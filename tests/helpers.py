from io import BytesIO
from pathlib import Path

from PIL import Image, ImageMath, ImageOps

from pillow_heif import HeifFile

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None  # pragma: no cover


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


def assert_image_similar(a, b, epsilon=0):
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


def create_heif(size: tuple = None, thumb_boxes: list = None, n_images=1, **kwargs) -> BytesIO:
    if size is None:
        size = (512, 512)
    if thumb_boxes is None:
        thumb_boxes = []
    im_heif = HeifFile()
    for i in range(n_images):
        im_heif.add_from_pillow(Image.effect_mandelbrot(size, (-3, -2.5, 2, 2.5), 100))
        size = (int(size[0] / 2), int(size[1] / 2))
        im_heif[i].add_thumbnails(thumb_boxes)
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
