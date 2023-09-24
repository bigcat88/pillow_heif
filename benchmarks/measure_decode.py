import sys
from time import perf_counter

import numpy as np
from PIL import Image

import pillow_heif

PILLOW_LOAD = 0
NUMPY_BGR = 1
NUMPY_RGB = 2


if __name__ == "__main__":
    pillow_heif.register_heif_opener()
    start_time = perf_counter()
    if int(sys.argv[3]) == PILLOW_LOAD:
        for _ in range(int(sys.argv[1])):
            im = Image.open(sys.argv[2])
            im.load()
    elif int(sys.argv[3]) == NUMPY_BGR:
        for _ in range(int(sys.argv[1])):
            if pillow_heif.__version__.startswith("0.1"):
                im = pillow_heif.open_heif(sys.argv[2], bgr_mode=True, convert_hdr_to_8bit=False)
            else:
                im = pillow_heif.open_heif(sys.argv[2], convert_hdr_to_8bit=False)
                im.convert_to("BGR" if im.bit_depth == 8 else "BGR;16")
            np_array = np.asarray(im)
    elif int(sys.argv[3]) == NUMPY_RGB:
        for _ in range(int(sys.argv[1])):
            if pillow_heif.__version__.startswith("0.1"):
                im = pillow_heif.open_heif(sys.argv[2], convert_hdr_to_8bit=False)
            else:
                im = pillow_heif.open_heif(sys.argv[2], convert_hdr_to_8bit=False)
                if im.bit_depth != 8:
                    im.convert_to("RGB;16")
            np_array = np.asarray(im)
    total_time = perf_counter() - start_time
    print(total_time)
    sys.exit(0)
