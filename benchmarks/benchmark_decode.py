import sys
from enum import IntEnum
from os import path
from subprocess import run
from time import perf_counter

import matplotlib.pyplot as plt
from cpuinfo import get_cpu_info


class OperationType(IntEnum):
    PILLOW_LOAD = 0
    BGR_NUMPY = 1


VERSIONS = ["0.5.1", "0.6.1", "0.7.2", "0.8.0", "0.9.3", "0.10.0"]
N_ITER_SMALL = 100
N_ITER_LARGE = 50


def measure_decode(image, n_iterations, operation_type: int):
    measure_file = path.join(path.dirname(path.abspath(__file__)), "measure_decode.py")
    cmd = f"{sys.executable} {measure_file} {n_iterations} {image} {operation_type}".split()
    start_time = perf_counter()
    run(cmd, check=True)
    total_time = perf_counter() - start_time
    return total_time / n_iterations


if __name__ == "__main__":
    tests_images_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests/images/heif_other")
    cat_image_path = path.join(tests_images_path, "cat.hif")
    pug_image_path = path.join(tests_images_path, "pug.heic")
    large_image_path = "image_large.heic"
    cat_image_pillow_results = []
    cat_image_bgr_numpy_results = []
    pug_image_pillow_results = []
    pug_image_bgr_numpy_results = []
    large_image_pillow_results = []
    large_image_bgr_numpy_results = []
    for i, v in enumerate(VERSIONS):
        run(f"{sys.executable} -m pip install pillow-heif=={v}".split(), check=True)
        cat_image_pillow_results.append(measure_decode(cat_image_path, N_ITER_SMALL, OperationType.PILLOW_LOAD))
        cat_image_bgr_numpy_results.append(measure_decode(cat_image_path, N_ITER_SMALL, OperationType.BGR_NUMPY))
        pug_image_pillow_results.append(measure_decode(pug_image_path, N_ITER_SMALL, OperationType.PILLOW_LOAD))
        pug_image_bgr_numpy_results.append(measure_decode(pug_image_path, N_ITER_SMALL, OperationType.BGR_NUMPY))
        large_image_pillow_results.append(measure_decode(large_image_path, N_ITER_LARGE, OperationType.PILLOW_LOAD))
        large_image_bgr_numpy_results.append(measure_decode(large_image_path, N_ITER_LARGE, OperationType.BGR_NUMPY))
    fig, ax = plt.subplots()
    ax.plot(VERSIONS, cat_image_pillow_results, label="cat image(pillow)")
    ax.plot(VERSIONS, cat_image_bgr_numpy_results, label="cat image(bgr;16, numpy)")
    ax.plot(VERSIONS, pug_image_pillow_results, label="pug image(pillow)")
    ax.plot(VERSIONS, pug_image_bgr_numpy_results, label="pug image(bgr, numpy)")
    ax.plot(VERSIONS, large_image_pillow_results, label="large image(pillow)")
    ax.plot(VERSIONS, large_image_bgr_numpy_results, label="large image(bgr, numpy)")
    plt.ylabel("time to decode(s)")
    if sys.platform.lower() == "darwin":
        _os = "macOS"
    elif sys.platform.lower() == "win32":
        _os = "Windows"
    else:
        _os = "Linux"
    plt.xlabel(f"{_os} - {get_cpu_info()['brand_raw']}")
    ax.legend()
    plt.savefig(f"results_decode_{_os}.png")
