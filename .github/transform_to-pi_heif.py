# This script transform project to `pi-heif` in place. Should be used only with GA Actions.

import os

DEV_NAME_ADD = ""  # This is only for debugging purposes of this script.


# From project folder run: `python3 .github/transform_to-pi_heif.py`
if __name__ == "__main__":
    # change `pillow_heif` to `pi_heif`
    files_list = [
        "libheif/build.py",
        "setup.py",
        "docker/manylinux_armv7l_wheel.Dockerfile",
        "docker/test_wheels.Dockerfile",
        "MANIFEST.in",
    ]
    for dir_name in ("pillow_heif", "tests"):
        for x in os.listdir(dir_name):
            if x.endswith(".py"):
                files_list += [os.path.join(dir_name, x)]

    for file_name in files_list:
        with open(file_name, "r") as file:
            data = file.read()
            modified_data = data.replace("pillow_heif", "pi_heif")
        if modified_data != data:
            with open(file_name + DEV_NAME_ADD, "w") as file:
                file.write(modified_data)

    os.rename("pillow_heif", "pi_heif")
