# https://github.com/bigcat88/pillow_heif/issues/89

from io import BytesIO

import cv2  # noqa
from PIL import Image

from pillow_heif import from_pillow, libheif_info

print(libheif_info())
from_pillow(Image.linear_gradient(mode="L")).save(BytesIO(), format="HEIF")
