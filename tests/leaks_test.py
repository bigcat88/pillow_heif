import ctypes
import gc
import mmap
import sys
from contextlib import suppress
from io import BytesIO
from os import chdir, path
from pathlib import Path

import helpers
import pytest
from PIL import Image, ImageSequence

import pillow_heif

pytest.importorskip("pympler", reason="`pympler` not installed")
pytest.importorskip("numpy", reason="`numpy` not installed")

from pympler.process import ProcessMemoryInfo, is_available

chdir(path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests"))
pillow_heif.register_heif_opener()

# without a working backend `rss` is always 0, which would make the checks below pass silently
requires_rss = pytest.mark.skipif(not is_available(), reason="`pympler` cannot measure RSS on this platform")
requires_refcounting = pytest.mark.skipif(
    sys.implementation.name != "cpython", reason="memory is not freed deterministically"
)


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
@pytest.mark.skipif(helpers.RELEASE_TESTS_FLAG, reason="Skip when building release.")
@pytest.mark.parametrize("image", (Path("images/heif/zPug_3.heic"), Path("images/heif_other/pug.heic")))
def test_open_save_objects_leaks(image):
    from pympler import summary, tracker

    perform_open_save(1, image)
    gc.collect()
    _summary1 = tracker.SummaryTracker().create_summary()
    _summary1 = tracker.SummaryTracker().create_summary()  # noqa
    gc.collect()
    gc.set_debug(gc.DEBUG_SAVEALL)
    try:
        perform_open_save(5, image)
        gc.collect()
        gc.collect()
        gc.collect()
    finally:
        gc.set_debug(0)
    summary2 = tracker.SummaryTracker().create_summary()
    results = summary._sweep(summary.get_diff(_summary1, summary2))  # noqa
    if results:
        summary.print_(results)
        raise MemoryError("Potential memory leaks")


def _get_mem_usage() -> float:
    if sys.platform == "linux":
        # glibc keeps freed chunks in its arenas, give them back before measuring
        with suppress(OSError, AttributeError):  # AttributeError: musl has no `malloc_trim`
            ctypes.CDLL(None).malloc_trim(0)
    return ProcessMemoryInfo().rss / 1024 / 1024


def _assert_no_mem_growth(iteration, warmup: int, block: int, tolerance: float = 2.0) -> None:
    # A leak adds the same amount of memory in every block, while a one-time allocator
    # growth shows up only once, so the last block is the one that gets measured.
    for _ in range(warmup):
        iteration()
    gc.collect()
    after_warmup = _get_mem_usage()
    for _ in range(block):
        iteration()
    gc.collect()
    settled = _get_mem_usage()
    for _ in range(block):
        iteration()
    gc.collect()
    growth = _get_mem_usage() - settled
    assert growth <= tolerance, (
        f"memory usage grew by {growth:.2f} MiB during the last {block} iterations "
        f"({after_warmup:.2f} MiB after warmup, {settled:.2f} MiB after the first block)"
    )


@requires_rss
def test_mem_growth_is_detected():
    # guards the checks below: they are only meaningful if a leak of this size fails them.
    # `mmap` is used instead of a plain allocation, as it is not served from the allocator
    # free lists, that on macOS stay accounted as resident and can hide a small leak.
    leaked = []

    def iteration():
        chunk = mmap.mmap(-1, 64 * 1024)
        chunk.write(b"x" * (64 * 1024))
        leaked.append(chunk)

    try:
        with pytest.raises(AssertionError, match="memory usage grew"):
            _assert_no_mem_growth(iteration, warmup=10, block=100)
    finally:
        for chunk in leaked:
            chunk.close()


@requires_rss
@requires_refcounting
def test_open_to_numpy_mem_leaks():
    import numpy as np

    image_path = Path("images/heif/L_10__29x100.heif")

    def iteration():
        heif_file = pillow_heif.open_heif(image_path, convert_hdr_to_8bit=False)
        np.asarray(heif_file[0])

    _assert_no_mem_growth(iteration, warmup=100, block=1000)


@requires_rss
@requires_refcounting
@pytest.mark.parametrize(
    "im, cp_type", [("images/heif_other/cat.hif", "NCLX"), ("images/heif_other/arrow.heic", "ICC")]
)
def test_color_profile_leaks(im, cp_type):
    heif_file = pillow_heif.open_heif(Path(im), convert_hdr_to_8bit=False)

    def iteration():
        _ = heif_file[0]._c_image.color_profile

    # a leaked color profile is small (~50 bytes for NCLX), so it needs many more iterations to show up
    _assert_no_mem_growth(iteration, warmup=1000, block=100000)


@requires_rss
@requires_refcounting
def test_metadata_leaks():
    heif_file = pillow_heif.open_heif(Path("images/heif_other/L_exif_xmp_iptc.heic"))

    def iteration():
        _ = heif_file[0]._c_image.metadata

    _assert_no_mem_growth(iteration, warmup=200, block=2000)


@requires_rss
@requires_refcounting
def test_pillow_plugin_leaks():
    # a `Path` and not a `BytesIO`: `BytesIO.read()` returns the same `bytes` object every time,
    # which would hide a leaked reference to the file data
    image_path = Path("images/heif/zPug_3.heic")

    def iteration():
        im = Image.open(image_path)
        for frame in ImageSequence.Iterator(im):
            frame.load()

    _assert_no_mem_growth(iteration, warmup=100, block=300)
