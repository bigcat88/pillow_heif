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
      aom \
      aom-dev \
      openjpeg-dev; \
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
      lsb-release && \
      echo "$(lsb_release -d)" && \
    if [$(lsb_release -d) ~= "ammy"]; then \
      echo "URA"; \
    fi \
  fi
