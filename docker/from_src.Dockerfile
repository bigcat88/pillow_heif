ARG DISTRO="alpine:3.14"

FROM ghcr.io/linuxserver/baseimage-${DISTRO}

COPY . /pillow_heif

RUN \
    apt-get update && \
    apt-get install -y build-essential yasm && \
    apt-get install -y python3-pip libfribidi-dev libharfbuzz-dev libjpeg-dev liblcms2-dev && \
    apt-get install -y libffi-dev libtool git && \
  python3 -m pip install --upgrade pip pytest && \
  python3 -m pip install -v pillow_heif/. && \
  echo "**** Build Done ****" && \
  pytest -s pillow_heif && \
  echo "**** Test Done ****" \
