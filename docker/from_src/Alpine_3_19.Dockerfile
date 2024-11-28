FROM alpine:3.19 as base

RUN \
  apk add --no-cache \
    python3-dev \
    py3-pip \
    alpine-sdk \
    cmake \
    nasm \
    aom-dev \
    x265-dev \
    py3-numpy \
    py3-pillow

FROM base as build_test

COPY . /pillow_heif

RUN \
  python3 -m venv --system-site-packages myenv && \
  source myenv/bin/activate && \
  python3 pillow_heif/libheif/linux_build_libs.py && \
  if [ `getconf LONG_BIT` = 64 ]; then \
    python3 -m pip install -v "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v "pillow_heif/.[tests-min]"; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest pillow_heif && \
  echo "**** Test Done ****"
