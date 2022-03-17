ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG INSTALL_CMD
RUN $INSTALL_CMD
ARG UPDATE_CMD
RUN $UPDATE_CMD

RUN python3 -m pip install pytest piexif cffi Pillow
RUN python3 -m pip install --only-binary=:all: pillow_heif
RUN cd .. && ls -la
