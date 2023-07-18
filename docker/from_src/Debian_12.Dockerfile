FROM debian:bookworm-slim as base

RUN \
  apt-get -qq update && \
  apt-get -y -q install \
    python3-pip \
    python3-pillow \
    libffi-dev \
    libtool \
    git \
    cmake \
    nasm \
    wget \
    libde265-dev \
    libx265-dev

FROM base as build_test

COPY . /pillow_heif

RUN \
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
