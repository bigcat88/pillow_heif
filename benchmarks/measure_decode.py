import sys

from PIL import Image

from pillow_heif import __version__, register_heif_opener

if __name__ == "__main__":
    _args = {}
    if __version__ != "0.1.6":
        _args["decode_threads"] = int(sys.argv[3])
    register_heif_opener(**_args)
    for i in range(int(sys.argv[1])):
        im = Image.open(sys.argv[2])
        im.load()
    sys.exit(0)
