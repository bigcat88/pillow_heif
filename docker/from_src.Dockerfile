FROM alpine:3.14

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
    aom aom-dev \
    openjpeg-dev && \
  python3 -m pip install --upgrade pip pytest && \
  ls -ls . && \
  git clone https://github.com/andrey1806/pillow_heif.git && \
  python3 -m pip install install -v pillow_heif/. && \
  echo "**** Build Done ****" && \
  pytest -s pillow_heif && \
  echo "**** Test Done ****"
