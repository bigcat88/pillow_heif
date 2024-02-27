FROM almalinux:9 as base

RUN \
  dnf install --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm -y && \
  dnf makecache && \
  dnf install -y python3 python3-devel python3-pip cmake && \
  dnf install -y x265-devel libaom-devel && \
  dnf groupinstall -y 'Development Tools'

RUN \
  python3 -m pip install --upgrade pip

FROM base as build_test

COPY . /pillow_heif

RUN \
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
