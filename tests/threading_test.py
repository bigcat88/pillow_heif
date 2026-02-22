"""Tests for thread safety of concurrent image decoding and encoding."""

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

import pytest
from helpers import hevc_enc
from PIL import Image

from pillow_heif import from_pillow, open_heif, options, register_heif_opener

np = pytest.importorskip("numpy", reason="NumPy not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Use 2 workers to avoid overwhelming libheif's internal decoder on free-threaded Python
N_WORKERS = 2
N_ITERATIONS = 3


@pytest.fixture(autouse=True)
def _single_decode_thread():
    """Use single decode thread per context to minimize internal thread contention.

    When multiple Python threads each trigger libheif decoding, setting
    decode threads to 0 ensures tile decoding happens in the calling
    thread rather than spawning additional background threads.
    """
    old = options.DECODE_THREADS
    options.DECODE_THREADS = 0
    yield
    options.DECODE_THREADS = old


def _decode_image(path):
    """Open and decode an image, returning basic properties."""
    heif_file = open_heif(path)
    data = bytes(heif_file.data)
    stride = heif_file.stride
    size = heif_file.size
    mode = heif_file.mode
    return len(data), stride, size, mode


@pytest.mark.parametrize(
    "img",
    (
        "images/heif/RGB_8__29x100.heif",
        "images/heif/RGB_8__128x128.heif",
        "images/heif/RGBA_8__29x100.heif",
    ),
)
def test_concurrent_decode_different_objects(img):
    """Multiple threads decode independent copies of the same file concurrently."""
    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_decode_image, img) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first = results[0]
    for result in results[1:]:
        assert result == first


def _access_shared_image_data(heif_image):
    """Access data and stride from a shared HeifImage object."""
    data = bytes(heif_image.data)
    stride = heif_image.stride
    size = heif_image.size
    return len(data), stride, size


@pytest.mark.parametrize(
    "img",
    (
        "images/heif/RGB_8__29x100.heif",
        "images/heif/RGB_8__128x128.heif",
    ),
)
def test_concurrent_access_shared_object(img):
    """Multiple threads access .data/.stride on the same object simultaneously.

    Tests the lazy decode race condition protection (_load_lock / decode_mutex).
    """
    heif_image = open_heif(img)

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_access_shared_image_data, heif_image) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first = results[0]
    for result in results[1:]:
        assert result == first


def test_concurrent_decode_data_integrity():
    """Decoded data is bit-identical regardless of concurrent access."""
    img = "images/heif/RGB_8__128x128.heif"
    ref = open_heif(img)
    ref_data = bytes(ref.data)
    ref_stride = ref.stride

    def _decode_and_compare(path):
        heif_image = open_heif(path)
        data = bytes(heif_image.data)
        stride = heif_image.stride
        assert data == ref_data
        assert stride == ref_stride
        return True

    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_decode_and_compare, img) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            assert future.result() is True


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
def test_concurrent_encode():
    """Multiple threads encode images concurrently."""

    def _encode_image():
        im = Image.linear_gradient(mode="L")
        heif_file = from_pillow(im)
        buf = BytesIO()
        heif_file.save(buf)
        buf.seek(0)
        result = open_heif(buf)
        return result.size, result.mode

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_encode_image) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first = results[0]
    for result in results[1:]:
        assert result == first


def test_concurrent_shared_object_data_integrity():
    """Multiple threads reading .data from the same unloaded object get identical bytes."""
    img = "images/heif/RGB_8__128x128.heif"
    heif_image = open_heif(img)

    def _read_data(image):
        return bytes(image.data)

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_read_data, heif_image) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first = results[0]
    for result in results[1:]:
        assert result == first


@pytest.mark.parametrize(
    "img",
    (
        "images/heif/L_8__128x128.heif",
        "images/heif/LA_8__128x128.heif",
        "images/heif/RGB_10__128x128.heif",
        "images/heif/RGBA_10__128x128.heif",
        "images/heif/RGB_12__128x128.heif",
    ),
)
def test_concurrent_decode_all_modes(img):
    """Concurrent decoding across different image modes (L, LA, 10-bit, 12-bit)."""
    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_decode_image, img) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first = results[0]
    for result in results[1:]:
        assert result == first


def test_concurrent_decode_mixed_formats():
    """Multiple threads decode different format images simultaneously."""
    images = [
        "images/heif/L_8__128x128.heif",
        "images/heif/RGB_8__128x128.heif",
        "images/heif/RGBA_8__128x128.heif",
        "images/heif/RGB_10__128x128.heif",
    ]

    results = {}
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = {}
        for img in images:
            for _ in range(N_ITERATIONS):
                f = executor.submit(_decode_image, img)
                futures[f] = img
        for future in as_completed(futures):
            img = futures[future]
            result = future.result()
            if img in results:
                assert result == results[img], f"Inconsistent result for {img}"
            else:
                results[img] = result


def test_concurrent_shared_object_size_consistency():
    """Verify .size is consistent after concurrent lazy decode.

    Regression test: if _data is published before .size is updated,
    a concurrent reader could see stale size with valid data.
    """
    img = "images/heif/RGB_8__128x128.heif"

    def _check_size_data(image, barrier):
        barrier.wait()
        data = bytes(image.data)
        size = image.size
        stride = image.stride
        assert len(data) == size[1] * stride
        return size, stride, len(data)

    for _ in range(5):
        heif_image = open_heif(img)
        barrier = threading.Barrier(N_WORKERS)

        results = []
        with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
            futures = [executor.submit(_check_size_data, heif_image, barrier) for _ in range(N_WORKERS)]
            for future in as_completed(futures):
                results.append(future.result())

        first = results[0]
        for result in results[1:]:
            assert result == first


def test_concurrent_to_pillow():
    """Multiple threads calling to_pillow() on the same unloaded image."""
    img = "images/heif/RGB_8__128x128.heif"
    heif_image = open_heif(img)

    def _to_pillow(image):
        pil_img = image.to_pillow()
        return pil_img.size, pil_img.mode, pil_img.tobytes()

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_to_pillow, heif_image) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first_size, first_mode, first_bytes = results[0]
    for size, mode, data in results[1:]:
        assert size == first_size
        assert mode == first_mode
        assert data == first_bytes


def test_concurrent_to_pillow_independent():
    """Multiple threads each open a file and convert to Pillow independently."""
    img = "images/heif/RGBA_8__128x128.heif"

    def _open_and_convert(path):
        heif_file = open_heif(path)
        pil_img = heif_file.to_pillow()
        return pil_img.size, pil_img.mode, pil_img.tobytes()

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_open_and_convert, img) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first = results[0]
    for result in results[1:]:
        assert result == first


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
def test_concurrent_encode_and_decode():
    """Encoding and decoding happen simultaneously in different threads."""
    img_path = "images/heif/RGB_8__128x128.heif"

    def _decode(path):
        heif_file = open_heif(path)
        return len(bytes(heif_file.data)), heif_file.size, heif_file.mode

    def _encode():
        im = Image.linear_gradient(mode="L")
        heif_file = from_pillow(im)
        buf = BytesIO()
        heif_file.save(buf)
        return len(buf.getvalue())

    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        decode_futures = [executor.submit(_decode, img_path) for _ in range(N_ITERATIONS)]
        encode_futures = [executor.submit(_encode) for _ in range(N_ITERATIONS)]

        decode_results = []
        for future in as_completed(decode_futures):
            decode_results.append(future.result())
        for future in as_completed(encode_futures):
            assert future.result() > 0

    first = decode_results[0]
    for result in decode_results[1:]:
        assert result == first


@pytest.mark.skipif(not hevc_enc(), reason="No HEVC encoder.")
def test_concurrent_encode_decode_roundtrip():
    """Concurrent encode-then-decode roundtrips produce consistent results."""

    def _roundtrip():
        im = Image.linear_gradient(mode="L")
        heif_file = from_pillow(im)
        buf = BytesIO()
        heif_file.save(buf)
        buf.seek(0)
        result = open_heif(buf)
        data = bytes(result.data)
        return result.size, result.mode, len(data), data

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_roundtrip) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first_size, first_mode, first_len, first_data = results[0]
    for size, mode, length, data in results[1:]:
        assert size == first_size
        assert mode == first_mode
        assert length == first_len
        assert data == first_data


def test_concurrent_multi_image_file():
    """Concurrent access to different images within the same multi-image HEIF file."""
    img = "images/heif/zPug_3.heic"
    if not os.path.exists(img):
        pytest.skip("Multi-image test file not available")

    heif_file = open_heif(img)
    if len(heif_file) < 2:
        pytest.skip("Test file has fewer than 2 images")

    def _decode_frame(frame_index):
        frame = heif_file[frame_index]
        data = bytes(frame.data)
        return frame.size, frame.mode, len(data)

    results_per_frame = {}
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = {}
        for frame_idx in range(len(heif_file)):
            for _ in range(N_ITERATIONS):
                f = executor.submit(_decode_frame, frame_idx)
                futures[f] = frame_idx
        for future in as_completed(futures):
            frame_idx = futures[future]
            result = future.result()
            if frame_idx in results_per_frame:
                assert result == results_per_frame[frame_idx]
            else:
                results_per_frame[frame_idx] = result


def test_concurrent_pillow_plugin_decode():
    """Concurrent decoding via the Pillow plugin interface."""
    register_heif_opener()

    img = "images/heif/RGB_8__128x128.heif"

    def _pillow_open(path):
        pil_img = Image.open(path)
        pil_img.load()
        return pil_img.size, pil_img.mode, pil_img.tobytes()

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_pillow_open, img) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first = results[0]
    for result in results[1:]:
        assert result == first


def test_concurrent_numpy_array_interface():
    """Concurrent access to __array_interface__ on a shared image."""
    img = "images/heif/RGB_8__128x128.heif"
    heif_image = open_heif(img)

    def _get_array(image):
        arr = np.array(image)
        return arr.shape, arr.dtype.str, arr.tobytes()

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = [executor.submit(_get_array, heif_image) for _ in range(N_WORKERS * N_ITERATIONS)]
        for future in as_completed(futures):
            results.append(future.result())

    first_shape, first_dtype, first_bytes = results[0]
    for shape, dtype, data in results[1:]:
        assert shape == first_shape
        assert dtype == first_dtype
        assert data == first_bytes


def test_stress_concurrent_decode():
    """Higher concurrency stress test with more threads and iterations."""
    img = "images/heif/RGB_8__128x128.heif"
    stress_workers = 4
    stress_iterations = 5

    results = []
    with ThreadPoolExecutor(max_workers=stress_workers) as executor:
        futures = [executor.submit(_decode_image, img) for _ in range(stress_workers * stress_iterations)]
        for future in as_completed(futures):
            results.append(future.result())

    first = results[0]
    for result in results[1:]:
        assert result == first


def test_concurrent_load_explicit():
    """Concurrent explicit load() calls on the same unloaded HeifImage."""
    img = "images/heif/RGB_8__128x128.heif"

    def _load(image, barrier, errors):
        try:
            barrier.wait()
            image.load()
            data = image.data
            assert data is not None
            assert image.size[0] > 0
            assert image.size[1] > 0
        except Exception as e:  # noqa # pylint: disable=broad-exception-caught
            errors.append(e)

    for _ in range(5):
        heif_file = open_heif(img)
        heif_image = heif_file[heif_file.primary_index]
        barrier = threading.Barrier(N_WORKERS)
        errors = []

        threads = [threading.Thread(target=_load, args=(heif_image, barrier, errors)) for _ in range(N_WORKERS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
        assert not errors, f"Errors in concurrent load: {errors}"
