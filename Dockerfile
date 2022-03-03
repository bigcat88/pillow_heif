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
    openjpeg-dev && \
  python3 -m pip install --upgrade pip && \
  git clone https://github.com/andrey18106/pillow_heif.git && \
  ls -la . && \
  pip install -v pillow_heif/. && \
  echo "**** Done ****"
