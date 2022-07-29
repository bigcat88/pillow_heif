import gc
import sys
from io import BytesIO
from os import chdir, path
from pathlib import Path
from platform import machine

import helpers
import pytest
from PIL import Image

import pillow_heif

pytest.importorskip("pympler", reason="`pympler` not installed")
pytest.importorskip("numpy", reason="`numpy` not installed")

print(pillow_heif.libheif_info())

chdir(path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests"))
pillow_heif.register_heif_opener()


def perform_open_save(iterations, image_path, do_save=True):
    for _ in range(iterations):
        image = Image.open(image_path)
        assert getattr(image, "heif_file") is not None
        if helpers.hevc_enc() and do_save:
            out_buf = BytesIO()
            image.save(out_buf, quality=20, format="HEIF", save_all=True)


@pytest.mark.skipif(sys.executable.lower().find("pypy") != -1, reason="Disabled on PyPy.")
@pytest.mark.parametrize("ctx_in_memory", (False, True))
def test_open_save_objects_leaks(ctx_in_memory):
    from pympler import summary, tracker

    pillow_heif.options().ctx_in_memory = ctx_in_memory
    image_path = Path("images/heif/zPug_3.heic")
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
@pytest.mark.parametrize("ctx_in_memory", (False, True))
def test_open_save_leaks(ctx_in_memory):
    pillow_heif.options().ctx_in_memory = ctx_in_memory
    mem_limit = None
    for i in range(1000):
        # do_save=False
        # https://bitbucket.org/multicoreware/x265_git/issues/616/x265_encoder_open-leaks-memory-zoneparam
        perform_open_save(1, Path("images/heif/zPug_3.heic"), do_save=False)
        gc.collect()
        mem = _get_mem_usage()
        if i < 300:
            mem_limit = mem + 1
            continue
        assert mem <= mem_limit, f"memory usage limit exceeded after {i + 1} iterations"


@pytest.mark.skipif(sys.platform.lower() == "win32", reason="requires Unix or macOS")
@pytest.mark.skipif(machine().find("x86_64") == -1, reason="run only on x86_64")
def test_open_to_numpy_mem_leaks():
    import numpy as np

    mem_limit = None
    im_path = Path("images/heif/zPug_3.heic")
    for i in range(500):
        heif_file = pillow_heif.open_heif(im_path)
        _array = np.asarray(heif_file[0])  # noqa
        _array = None  # noqa
        gc.collect()
        mem = _get_mem_usage()
        if i < 300:
            mem_limit = mem + 1
            continue
        assert mem <= mem_limit, f"memory usage limit exceeded after {i + 1} iterations"
