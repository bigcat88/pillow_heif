ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG UPDATE_CMD
RUN $UPDATE_CMD
ARG INSTALL_CMD
ARG OS_PACKAGES
RUN $INSTALL_CMD $OS_PACKAGES

RUN python3 -m pip install pytest piexif cffi Pillow
RUN python3 -m pip install --only-binary=:all: pillow_heif
