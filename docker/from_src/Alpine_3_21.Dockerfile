FROM alpine:3.21 as base

RUN \
  apk add --no-cache \
    python3-dev \
    py3-pip \
    alpine-sdk \
    libheif-dev \
    py3-numpy \
    py3-pillow

FROM base as build_test

COPY . /pillow_heif

RUN \
  python3 -m venv --system-site-packages myenv && \
  source myenv/bin/activate && \
  python3 -m pip install -v "pillow_heif/.[tests]"; \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest pillow_heif && \
  echo "**** Test Done ****"
