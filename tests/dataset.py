import os
from pathlib import Path
from warnings import warn

import helpers

os.chdir(os.path.dirname(os.path.abspath(__file__)))


CORRUPTED_DATASET = list(Path().glob("images/heif_corrupted/?*.*"))
TRUNCATED_DATASET = list(Path().glob("images/heif_truncated/?*.*"))
MINIMAL_DATASET = list(Path().glob("images/heif/?*.*"))
FULL_DATASET = MINIMAL_DATASET + list(Path().glob("images/heif_other/**/?*.*"))

CORRUPTED_DATASET = [i for i in CORRUPTED_DATASET if not i.name.endswith(".txt")]
TRUNCATED_DATASET = [i for i in TRUNCATED_DATASET if not i.name.endswith(".txt")]
MINIMAL_DATASET = [i for i in MINIMAL_DATASET if not i.name.endswith(".txt")]
FULL_DATASET = [i for i in FULL_DATASET if not i.name.endswith(".txt")]

if not helpers.aom():
    warn("Skipping tests for `AVIF` format due to lack of codecs.", stacklevel=1)
    CORRUPTED_DATASET = [i for i in CORRUPTED_DATASET if not i.name.endswith(".avif")]
    TRUNCATED_DATASET = [i for i in TRUNCATED_DATASET if not i.name.endswith(".avif")]
    MINIMAL_DATASET = [i for i in MINIMAL_DATASET if not i.name.endswith(".avif")]
    FULL_DATASET = [i for i in FULL_DATASET if not i.name.endswith(".avif")]
