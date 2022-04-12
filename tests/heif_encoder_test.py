import os
from io import BytesIO
from pathlib import Path

import pytest

from pillow_heif import _options  # noqa
from pillow_heif import (
    HeifError,
    HeifSaveMask,
    open_heif,
    options,
    register_heif_opener,
)

imagehash = pytest.importorskip("hashes_test", reason="NumPy not installed")


os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_scale():
    heic_file = open_heif(Path("images/pug_1_0.heic"))
    heic_file.scale(640, 640)
    out_buffer = BytesIO()
    heic_file.save(out_buffer)
    imagehash.compare_hashes([Path("images/pug_1_0.heic"), out_buffer], max_difference=1)


@pytest.mark.skipif(not options().hevc_enc, reason="No HEVC encoder.")
def test_save_empty():
    heic_file = open_heif(Path("images/pug_1_0.heic"))
    save_mask = heic_file.get_img_thumb_mask_for_save(HeifSaveMask.SAVE_NONE)
    out_buffer = BytesIO()
    with pytest.raises(ValueError):
        heic_file.save(out_buffer, save_mask=save_mask)


def test_no_encoder():
    try:
        _options.CFG_OPTIONS._hevc_enc = False
        heic_file = open_heif(Path("images/pug_1_0.heic"))
        out_buffer = BytesIO()
        with pytest.raises(HeifError):
            heic_file.save(out_buffer)
    finally:
        _options.CFG_OPTIONS = _options.PyLibHeifOptions()
