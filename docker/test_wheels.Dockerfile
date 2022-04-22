ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG PREPARE_CMD
RUN $PREPARE_CMD
ARG INSTALL_CMD
RUN $INSTALL_CMD

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pytest piexif cffi pillow numpy pympler defusedxml
RUN python3 -m pip install --no-deps --only-binary=:all: pillow_heif

COPY . /pillow_heif

RUN python3 -m pytest -rs -v pillow_heif/. && echo "**** Test Done ****" && python3 -m pip show pillow_heif
