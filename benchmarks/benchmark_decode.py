import sys
from enum import IntEnum
from os import path
from subprocess import run

import matplotlib.pyplot as plt
from cpuinfo import get_cpu_info


class OperationType(IntEnum):
    PILLOW_LOAD = 0
    NUMPY_BGR = 1
    NUMPY_RGB = 2


VERSIONS = ["0.7.2", "0.8.0", "0.9.3", "0.11.1", "0.12.0"]
N_ITER_SMALL = 100
N_ITER_LARGE = 50


def measure_decode(image, n_iterations, op_type: int):
    measure_file = path.join(path.dirname(path.abspath(__file__)), "measure_decode.py")
    cmd = f"{sys.executable} {measure_file} {n_iterations} {image} {op_type}".split()
    result = run(cmd, check=True, capture_output=True)
    return float(result.stdout.decode(encoding="utf-8").strip()) / n_iterations


if __name__ == "__main__":  # argv: OperationType
    operation_type = OperationType(int(sys.argv[1]))
    print(f"Operation type: {operation_type}")
    tests_images_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests/images/heif_other")
    cat_image_path = path.join(tests_images_path, "cat.hif")
    pug_image_path = path.join(tests_images_path, "pug.heic")
    large_image_path = "image_large.heic"
    cat_image_results = []
    pug_image_results = []
    large_image_results = []
    for v in VERSIONS:
        run(f"{sys.executable} -m pip install pillow-heif=={v}".split(), check=True)
        cat_image_results.append(measure_decode(cat_image_path, N_ITER_SMALL, operation_type))
        pug_image_results.append(measure_decode(pug_image_path, N_ITER_SMALL, operation_type))
        large_image_results.append(measure_decode(large_image_path, N_ITER_LARGE, operation_type))
    fig, ax = plt.subplots()
    ax.plot(VERSIONS, cat_image_results, label="cat image")
    ax.plot(VERSIONS, pug_image_results, label="pug image")
    ax.plot(VERSIONS, large_image_results, label="large image")
    plt.ylabel("time to decode(s)")
    if sys.platform.lower() == "darwin":
        _os = "macOS"
    elif sys.platform.lower() == "win32":
        _os = "Windows"
    else:
        _os = "Linux"
    plt.xlabel(f"{_os} - {get_cpu_info()['brand_raw']}")
    ax.legend()
    plt.savefig(f"results_decode_{operation_type.name.lower()}_{_os}.png", dpi=200)
