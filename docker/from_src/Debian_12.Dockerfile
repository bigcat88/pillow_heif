FROM debian:bookworm-slim as base

RUN \
  apt-get -qq update && \
  apt-get -y -q install \
    python3-pip \
    python3-dev \
    python3-setuptools \
    libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev \
    libffi-dev \
    libtool \
    git \
    cmake \
    nasm \
    wget \
    libde265-dev \
    libx265-dev \
    libaom-dev

FROM base as build_test

COPY . /pillow_heif

RUN \
  python3 pillow_heif/libheif/linux_build_libs.py && \
  if [ `getconf LONG_BIT` = 64 ]; then \
    python3 -m pip install -v --break-system-packages "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v --break-system-packages "pillow_heif/.[tests-min]"; \
    export PH_TESTS_NO_HEVC_ENC=1; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest pillow_heif && \
  echo "**** Test Done ****"
