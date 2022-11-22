FROM debian:buster-slim as base

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
    wget \
    automake \
    cmake

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
  pytest -s pillow_heif && \
  echo "**** Test Done ****"
