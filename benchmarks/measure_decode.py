import sys

import numpy as np
from PIL import Image

import pillow_heif

PILLOW_LOAD = 0
BGR_NUMPY = 1


if __name__ == "__main__":
    if int(sys.argv[3]) == PILLOW_LOAD:
        pillow_heif.register_heif_opener()
        for i in range(int(sys.argv[1])):
            im = Image.open(sys.argv[2])
            im.load()
    elif int(sys.argv[3]) == BGR_NUMPY:
        for i in range(int(sys.argv[1])):
            if pillow_heif.__version__ in ("0.10.0",):
                im = pillow_heif.open_heif(sys.argv[2], bgr_mode=True, convert_hdr_to_8bit=False)
            else:
                im = pillow_heif.open_heif(sys.argv[2], convert_hdr_to_8bit=False)
                im.convert_to("BGR" if im.bit_depth == 8 else "BGR;16")
            np_array = np.asarray(im)
    sys.exit(0)
