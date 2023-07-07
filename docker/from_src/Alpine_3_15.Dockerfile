FROM alpine:3.15 as base

RUN \
  apk add --no-cache \
    python3-dev \
    py3-pip \
    perl \
    alpine-sdk \
    libffi-dev \
    cmake \
    nasm \
    libde265-dev \
    py3-numpy \
    py3-pillow

RUN \
  python3 -m pip install --upgrade pip

FROM base as build_test

COPY . /pillow_heif

RUN \
  if [ `uname -m` = "x86_64" ]; then \
    python3 -m pip install -v "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v "pillow_heif/.[tests-min]"; \
    export PH_TESTS_NO_HEVC_ENC=1; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest -rs pillow_heif && \
  echo "**** Test Done ****"
