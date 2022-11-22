FROM debian:buster-slim

COPY . /pillow_heif

RUN \
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
    wget \
    autoconf \
    automake \
    cmake && \
  python3 -m pip install --upgrade pip && \
  echo "**** Installing patchelf ****" && \
  git clone -b 0.17.0 https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make check && make install && \
  cd .. && \
  echo "**** Install python build dependencies ****" && \
  python3 -m pip install cffi pytest && \
  echo "**** Start building ****" && \
  cd pillow_heif && \
  python3 setup.py bdist_wheel && \
  echo "**** Repairing wheel ****" && \
  python3 -m pip install auditwheel && \
  auditwheel repair -w repaired_dist/ dist/*.whl --plat manylinux_2_28_armv7l && \
  echo "**** Testing wheel ****" && \
  python3 -m pip install repaired_dist/*.whl && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3 -m pytest -rs && \
  echo "**** Build Done ****"
