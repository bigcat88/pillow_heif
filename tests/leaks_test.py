import gc
import sys
from io import BytesIO
from os import chdir, path
from pathlib import Path

import pytest
from PIL import Image

import pillow_heif

pytest.importorskip("pympler", reason="`pympler` not installed")

print(pillow_heif.libheif_info())

chdir(path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests"))
pillow_heif.register_heif_opener()


def perform_open_save(value):
    for _ in range(value):
        image = Image.open(Path("images/nokia/alpha_3_2.heic"))
        assert getattr(image, "heif_file") is not None
        if pillow_heif.options().hevc_enc:
            out_buf = BytesIO()
            image.save(out_buf, quality=20, format="HEIF")


@pytest.mark.skipif(sys.executable.lower().find("pypy") != -1, reason="Disabled on PyPy.")
def test_open_leaks():
    from pympler import summary, tracker

    perform_open_save(1)
    gc.collect()
    _summary1 = tracker.SummaryTracker().create_summary()
    _summary1 = tracker.SummaryTracker().create_summary()  # noqa
    gc.collect()
    gc.set_debug(gc.DEBUG_SAVEALL)
    perform_open_save(3)
    gc.collect()
    summary2 = tracker.SummaryTracker().create_summary()
    results = summary._sweep(summary.get_diff(_summary1, summary2))  # noqa
    summary.print_(results)
    for result in results:
        # look for strings like: `_cffi_backend.__CDataGCP`, `_cffi_backend.__CDataOwnGC`
        assert result[0].find("cffi") == -1
        # look for strings like: `pillow_heif._libheif_ctx.LibHeifCtx`
        assert result[0].find("pillow_heif") == -1
