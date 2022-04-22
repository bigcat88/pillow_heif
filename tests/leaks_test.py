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


def perform_open_save(iterations, image_path, do_save=True):
    for _ in range(iterations):
        image = Image.open(image_path)
        assert getattr(image, "heif_file") is not None
        if pillow_heif.options().hevc_enc and do_save:
            out_buf = BytesIO()
            image.save(out_buf, quality=20, format="HEIF", save_all=True)


@pytest.mark.skipif(sys.executable.lower().find("pypy") != -1, reason="Disabled on PyPy.")
def test_open_save_objects_leaks():
    from pympler import summary, tracker

    image_path = Path("images/rgb8_128_128_2_1.heic")
    perform_open_save(1, image_path)
    gc.collect()
    _summary1 = tracker.SummaryTracker().create_summary()
    _summary1 = tracker.SummaryTracker().create_summary()  # noqa
    gc.collect()
    gc.set_debug(gc.DEBUG_SAVEALL)
    perform_open_save(5, image_path)
    gc.collect()
    summary2 = tracker.SummaryTracker().create_summary()
    results = summary._sweep(summary.get_diff(_summary1, summary2))  # noqa
    summary.print_(results)
    for result in results:
        # look for strings like: `_cffi_backend.__CDataGCP`, `_cffi_backend.__CDataOwnGC`
        assert result[0].find("cffi") == -1
        # look for strings like: `pillow_heif._libheif_ctx.LibHeifCtx`
        assert result[0].find("pillow_heif") == -1


def _get_mem_usage():
    from resource import RUSAGE_SELF, getpagesize, getrusage

    mem = getrusage(RUSAGE_SELF).ru_maxrss
    return mem * getpagesize() / 1024 / 1024


@pytest.mark.skipif(sys.platform.lower() == "win32", reason="requires Unix or macOS")
def test_open_save_leaks():
    mem_limit = None
    for i in range(750):
        # do_save=False
        # Reason: https://bitbucket.org/multicoreware/x265_git/issues/616/x265_encoder_open-leaks-memory-zoneparam
        perform_open_save(1, Path("images/rgb8_128_128_2_1.heic"), do_save=False)
        mem = _get_mem_usage()
        if i < 250:
            mem_limit = mem + 1
            continue
        assert mem <= mem_limit, f"memory usage limit exceeded after {i + 1} iterations"
