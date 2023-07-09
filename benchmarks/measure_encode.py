import sys
from io import BytesIO
from os import path
from time import perf_counter

from PIL import Image

from pillow_heif import register_heif_opener

L_IMAGE = Image.effect_mandelbrot((4096, 4096), (-3, -2.5, 2, 2.5), 100)
LA_IMAGE = Image.merge("LA", [L_IMAGE, L_IMAGE.transpose(Image.ROTATE_90)])
RGB_IMAGE = Image.merge("RGB", [L_IMAGE, L_IMAGE.transpose(Image.ROTATE_90), L_IMAGE.transpose(Image.ROTATE_180)])
RGBA_IMAGE = Image.merge(
    "RGBA",
    [
        L_IMAGE,
        L_IMAGE.transpose(Image.ROTATE_90),
        L_IMAGE.transpose(Image.ROTATE_180),
        L_IMAGE.transpose(Image.ROTATE_270),
    ],
)


if __name__ == "__main__":
    _args = {}
    register_heif_opener(**_args)
    if sys.argv[2] == "PUG":
        tests_images_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests/images/heif_other")
        img = Image.open(path.join(tests_images_path, "pug.heic"))
    elif sys.argv[2] == "RGBA":
        img = RGBA_IMAGE
    elif sys.argv[2] == "RGB":
        img = RGB_IMAGE
    elif sys.argv[2] == "LA":
        img = LA_IMAGE
    else:
        img = L_IMAGE
    start_time = perf_counter()
    for i in range(int(sys.argv[1])):
        buf = BytesIO()
        img.save(buf, format="HEIF")
    total_time = perf_counter() - start_time
    print(total_time)
    sys.exit(0)
