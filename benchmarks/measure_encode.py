import sys
from io import BytesIO

from PIL import Image

from pillow_heif import __version__, register_heif_opener

L_IMAGE = Image.effect_mandelbrot((4096, 4096), (-3, -2.5, 2, 2.5), 100)
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
    if sys.argv[2] == "RGBA":
        img = RGBA_IMAGE
    elif sys.argv[2] == "RGB":
        img = RGB_IMAGE
    else:
        if __version__ == "0.2.1":
            img = RGB_IMAGE
        else:
            img = L_IMAGE
    for i in range(int(sys.argv[1])):
        buf = BytesIO()
        img.save(buf, format="HEIF")
    sys.exit(0)
