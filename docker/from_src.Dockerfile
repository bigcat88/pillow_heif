ARG DISTRO="alpine:3.14"

FROM ghcr.io/linuxserver/baseimage-${DISTRO}

COPY . /pillow_heif

RUN \
  if [ -f /sbin/apk ]; then \
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
      py3-numpy; \
  elif [ -f /usr/bin/apt ]; then \
    apt-get update && \
    apt-get install -y \
      python3-pip \
      libfribidi-dev \
      libharfbuzz-dev \
      libjpeg-dev \
      liblcms2-dev \
      libffi-dev \
      libtool \
      git \
      cmake \
      lsb-release; \
      lsb_release -r | grep -q "20.04" || apt-get install -y nasm; \
  fi && \
  python3 -m pip install --upgrade pip && \
  python3 -m pip install -v "pillow_heif/.[tests]" && \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest -s pillow_heif && \
  echo "**** Test Done ****"
