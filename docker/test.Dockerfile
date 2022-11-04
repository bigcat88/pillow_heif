FROM alpine:3.14

COPY . /pillow_heif

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
    autoconf \
    automake \
    cmake \
    nasm \
    py3-numpy \
    py3-pillow && \
  python3 -m pip install --upgrade pip && \
  echo "**** Installing patchelf ****" && \
  git clone https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make check && make install && \
  cd .. && \
  echo "**** Install python build dependencies ****" && \
  python3 -m pip install cffi pytest wheel && \
  echo "**** Start building ****" && \
  cd pillow_heif && \
  python3 setup.py bdist_wheel && \
  echo "**** Repairing wheel ****" && \
  python3 -m pip install auditwheel && \
  auditwheel repair -w repaired_dist/ dist/*.whl && \
  echo "**** Testing wheel ****" && \
  python3 -m pip install repaired_dist/*.whl && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3 -m pytest -rs && \
  echo "**** Build Done ****"
