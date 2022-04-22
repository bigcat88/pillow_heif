import os
from pathlib import Path
from warnings import warn

from pillow_heif import options

os.chdir(os.path.dirname(os.path.abspath(__file__)))

AVIF_IMAGES = [i for i in Path().glob("images/**/*.avif") if i.parent.name.find("corrupted") == -1]
HEIC_IMAGES = [i for i in Path().glob("images/**/*.heic") if i.parent.name.find("corrupted") == -1]
HEIF_IMAGES = [i for i in Path().glob("images/**/*.heif") if i.parent.name.find("corrupted") == -1] + [
    i for i in Path().glob("images/**/*.hif") if i.parent.name.find("corrupted") == -1
]
MINIMAL_DATASET = [i for i in Path().glob("images/*.*") if i.name[0] != "."]

if not options().avif:
    warn("Skipping tests for `AV1` format due to lack of codecs.")
    AVIF_IMAGES.clear()
    MINIMAL_DATASET = [i for i in MINIMAL_DATASET if not i.name.endswith(".avif")]

FULL_DATASET = AVIF_IMAGES + HEIC_IMAGES + HEIF_IMAGES
CORRUPTED_DATASET = list(Path().glob("images/corrupted/*.*"))
