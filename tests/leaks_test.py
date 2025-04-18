import gc
import sys
from io import BytesIO
from os import chdir, path
from pathlib import Path
from platform import machine

import helpers
import pytest
from PIL import Image, ImageSequence

import pillow_heif

pytest.importorskip("pympler", reason="`pympler` not installed")
pytest.importorskip("numpy", reason="`numpy` not installed")

chdir(path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests"))
pillow_heif.register_heif_opener()


def perform_open_save(iterations, image_path):
    for _ in range(iterations):
        image = Image.open(image_path)
        assert getattr(image, "_heif_file") is not None
        if helpers.hevc_enc():
            out_buf = BytesIO()
            image.save(out_buf, quality=20, format="HEIF", save_all=True)


@pytest.mark.skipif(sys.platform.lower() == "win32", reason="Disabled on Windows.")
@pytest.mark.skipif(sys.executable.lower().find("pypy") != -1, reason="Disabled on PyPy.")
@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("image", (Path("images/heif/zPug_3.heic"), Path("images/heif_other/pug.heic")))
def test_open_save_objects_leaks(image):
    from pympler import summary, tracker

    image_file_data = BytesIO(Path(image).read_bytes())
    perform_open_save(1, image_file_data)
    gc.collect()
    _summary1 = tracker.SummaryTracker().create_summary()
    _summary1 = tracker.SummaryTracker().create_summary()  # noqa
    gc.collect()
    gc.set_debug(gc.DEBUG_SAVEALL)
    perform_open_save(6, image_file_data)
    gc.collect()
    gc.collect()
    gc.collect()
    summary2 = tracker.SummaryTracker().create_summary()
    results = summary._sweep(summary.get_diff(_summary1, summary2))  # noqa
    if results:
        summary.print_(results)
        raise MemoryError("Potential memory leaks")


def _get_mem_usage():
    from resource import RUSAGE_SELF, getpagesize, getrusage

    mem = getrusage(RUSAGE_SELF).ru_maxrss
    return mem * getpagesize() / 1024 / 1024


@pytest.mark.skipif(sys.platform.lower() in ("win32", "darwin"), reason="run only on Linux")
@pytest.mark.skipif(machine().find("x86_64") == -1, reason="run only on x86_64")
def test_open_to_numpy_mem_leaks():
    import numpy as np

    mem_limit = None
    image_file_data = BytesIO(Path("images/heif/L_10__29x100.heif").read_bytes())
    for i in range(1000):
        heif_file = pillow_heif.open_heif(image_file_data, convert_hdr_to_8bit=False)
        _array = np.asarray(heif_file[0])  # noqa
        _array = None  # noqa
        gc.collect()
        mem = _get_mem_usage()
        if i < 100:
            mem_limit = mem + 2
            continue
        assert mem <= mem_limit, f"memory usage limit exceeded after {i + 1} iterations"


@pytest.mark.skipif(sys.platform.lower() in ("win32", "darwin"), reason="run only on Linux")
@pytest.mark.skipif(machine().find("x86_64") == -1, reason="run only on x86_64")
@pytest.mark.parametrize(
    "im, cp_type", [("images/heif_other/cat.hif", "NCLX"), ("images/heif_other/arrow.heic", "ICC")]
)
def test_color_profile_leaks(im, cp_type):
    mem_limit = None
    heif_file = pillow_heif.open_heif(Path(im), convert_hdr_to_8bit=False)
    for i in range(1200):
        _nclx = heif_file[0]._c_image.color_profile  # noqa
        _nclx = None  # noqa
        gc.collect()
        mem = _get_mem_usage()
        if i < 200:
            mem_limit = mem + 2
            continue
        assert mem <= mem_limit, f"memory usage limit exceeded after {i + 1} iterations. Color profile type:{cp_type}"


@pytest.mark.skipif(sys.platform.lower() in ("win32", "darwin"), reason="run only on Linux")
@pytest.mark.skipif(machine().find("x86_64") == -1, reason="run only on x86_64")
def test_metadata_leaks():
    mem_limit = None
    heif_file = pillow_heif.open_heif(Path("images/heif_other/L_exif_xmp_iptc.heic"))
    for i in range(1000):
        _metadata = heif_file[0]._c_image.metadata  # noqa
        _metadata = None  # noqa
        gc.collect()
        mem = _get_mem_usage()
        if i < 100:
            mem_limit = mem + 2
            continue
        assert mem <= mem_limit, f"memory usage limit exceeded after {i + 1} iterations"


@pytest.mark.skipif(sys.platform.lower() in ("win32", "darwin"), reason="run only on Linux")
@pytest.mark.skipif(machine().find("x86_64") == -1, reason="run only on x86_64")
def test_pillow_plugin_leaks():
    mem_limit = None
    image_file_data = BytesIO(Path("images/heif/zPug_3.heic").read_bytes())
    for i in range(1000):
        im = Image.open(image_file_data)
        for frame in ImageSequence.Iterator(im):
            frame.load()
            frame = None  # noqa
        im = None  # noqa
        gc.collect()
        gc.collect()
        mem = _get_mem_usage()
        if i < 300:
            mem_limit = mem + 2
            continue
        assert mem <= mem_limit, f"memory usage limit exceeded after {i + 1} iterations"
