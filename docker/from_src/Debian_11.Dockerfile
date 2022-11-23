FROM debian:bullseye-slim as base

RUN \
  apt-get -qq update && \
  apt-get -y -q install \
    python3-pip \
    libfribidi-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    liblcms2-dev \
    libffi-dev \
    libtool \
    git \
    cmake \
    nasm \
    wget \
    libde265-dev

RUN \
  python3 -m pip install --upgrade pip

RUN \
   python3 -m pip install Pillow==9.2.0 cffi==1.15.0

FROM base as build_test

COPY . /pillow_heif

RUN \
  if [ `uname -m` = "x86_64" ]; then \
    python3 -m pip install -v "pillow_heif/.[tests]"; \
  else \
    python3 -m pip install -v "pillow_heif/.[tests-min]"; \
  fi && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest -s pillow_heif && \
  echo "**** Test Done ****"
