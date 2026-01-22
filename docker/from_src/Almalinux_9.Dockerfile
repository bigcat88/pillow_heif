FROM almalinux:9 as base

RUN \
  dnf install --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm -y && \
  dnf makecache && \
  dnf install -y python3.11 python3.11-devel python3.11-pip cmake && \
  dnf install -y x265-devel libaom-devel && \
  dnf groupinstall -y 'Development Tools'

RUN \
  python3.11 -m pip install --upgrade pip

FROM base as build_test

COPY . /pillow_heif

RUN \
  python3.11 pillow_heif/libheif/build_libs.py && \
  python3.11 -m pip install -v "pillow_heif/.[tests]"; \
  echo "**** Build Done ****" && \
  python3.11 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest pillow_heif && \
  echo "**** Test Done ****"
