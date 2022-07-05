FROM ghcr.io/linuxserver/baseimage-ubuntu:focal

COPY . /pillow_heif

RUN \
  apt-get update && \
  apt-get install -y \
    python3-pip \
    libfribidi-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    liblcms2-dev \
    libffi-dev \
    libtool \
    git \
    cmake && \
  python3 -m pip install --upgrade pip && \
  echo "**** Start building ****" && \
  ls -la && \
  cd pillow_heif && \
  python3 setup.py bdist_wheel && \
  echo "**** Repairing wheel ****" && \
  python3 -m pip install auditwheel && \
  echo "**** Testing wheel ****" && \
  echo "**** Build Done ****" && \
  ls -la && ls -la dist
