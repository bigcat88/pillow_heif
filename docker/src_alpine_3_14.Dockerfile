FROM ghcr.io/linuxserver/baseimage-alpine:3.14

COPY . /pillow_heif

RUN \
  apk add --no-cache \
    py3-pip \
    python3-dev \
    libtool \
    git \
    gcc \
    m4 \
    perl \
    alpine-sdk \
    cmake \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    openjpeg-dev \
    nasm \
    libde265-dev \
    py3-numpy \
    py3-pillow && \
  python3 -m pip install --upgrade pip && \
  if [ `getconf LONG_BIT` = 64 ]; then \
    python3 -m pip install -v "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v "pillow_heif/.[tests-min]"; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  if [ `uname -m` != "x86_64" ]; then \
    export PH_TESTS_NO_HEVC_ENC=1; \
  fi && \
  pytest -s pillow_heif && \
  echo "**** Test Done ****"
