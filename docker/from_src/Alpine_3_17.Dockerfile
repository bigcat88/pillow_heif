FROM alpine:3.17 as base

RUN \
  apk add --no-cache \
    py3-pip \
    python3-dev \
    perl \
    alpine-sdk \
    libffi-dev \
    cmake \
    nasm \
    aom-dev \
    py3-numpy \
    py3-pillow

RUN \
  python3 -m pip install --upgrade pip

RUN \
  python3 -m pip install wheel cffi==1.15.1

FROM base as build_test

COPY . /pillow_heif

RUN \
  if [ `getconf LONG_BIT` = 64 ]; then \
    python3 -m pip install -v "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v "pillow_heif/.[tests-min]"; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest -s pillow_heif && \
  echo "**** Test Done ****"
