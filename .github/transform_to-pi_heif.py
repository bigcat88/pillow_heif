"""Script to transform the project to `pi-heif` in place. Should be used only with GA Actions."""

import os
import pathlib

DEV_NAME_ADD = ""  # This is only for debugging purposes of this script.


# From project folder run: `python3 .github/transform_to-pi_heif.py`
if __name__ == "__main__":
    # change `pillow_heif` to `pi_heif`
    files_list = [
        "setup.py",
        "docker/test_wheels.Dockerfile",
        "MANIFEST.in",
        "pillow_heif/_pillow_heif.c",
    ]
    for dir_name in ("pillow_heif", "tests"):
        for x in os.listdir(dir_name):
            if x.endswith(".py"):
                files_list += [os.path.join(dir_name, x)]

    for file_name in files_list:
        data = pathlib.Path(file_name).read_text(encoding="utf-8")
        modified_data = data.replace("pillow_heif", "pi_heif")
        if modified_data != data:
            pathlib.Path(file_name + DEV_NAME_ADD).write_text(modified_data)

    os.rename("pillow_heif/_pillow_heif.c", "pillow_heif/_pi_heif.c")
    os.rename("pillow_heif", "pi_heif")
