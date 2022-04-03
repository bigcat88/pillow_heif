import gc
from io import BytesIO
from os import chdir, path
from pathlib import Path

from PIL import Image
from pympler import summary, tracker

import pillow_heif

print(pillow_heif.libheif_info())

chdir(path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests"))
pillow_heif.register_heif_opener()


def perform_opens(value):
    for _ in range(value):
        image = Image.open(Path("images/nokia/alpha_3_2.heic"))
        assert image
        out_buf = BytesIO()
        image.save(out_buf, quality=20, format="HEIF")


def test_open_leaks():
    perform_opens(1)
    gc.collect()
    _summary1 = tracker.SummaryTracker().create_summary()
    _summary1 = tracker.SummaryTracker().create_summary()  # noqa
    gc.collect()
    gc.set_debug(gc.DEBUG_SAVEALL)
    perform_opens(3)
    gc.collect()
    summary2 = tracker.SummaryTracker().create_summary()
    results = summary._sweep(summary.get_diff(_summary1, summary2))  # noqa
    summary.print_(results)
    for result in results:
        # look for strings like: `_cffi_backend.__CDataGCP`, `_cffi_backend.__CDataOwnGC`
        assert result[0].find("cffi") == -1
        # look for strings like: `pillow_heif._libheif_ctx.LibHeifCtx`
        assert result[0].find("pillow_heif") == -1
