FROM ghcr.io/linuxserver/baseimage-ubuntu:jammy

COPY . /pillow_heif

RUN \
  apt-get update && apt-get install -y -q \
    python3-pip \
    libfribidi-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    liblcms2-dev \
    libffi-dev \
    libtool \
    git \
    pkg-config \
    autoconf \
    automake \
    cmake \
    nasm \
    libaom-dev \
    libde265-dev && \
  python3 -m pip install --upgrade pip && \
  if [ `getconf LONG_BIT` = 64 ]; then \
    python3 -m pip install -v "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v "pillow_heif/.[tests-min]"; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest -s pillow_heif && \
  echo "**** Test Done ****"
