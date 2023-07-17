ARG PY_VERSION

FROM python:$PY_VERSION-alpine3.15

COPY . /

RUN \
  apk add --no-cache \
    libtool \
    perl \
    alpine-sdk \
    cmake \
    autoconf \
    automake \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev

RUN \
  echo "**** Installing patchelf ****" && \
  git clone -b 0.17.2 https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make install && \
  cd ..

ARG PY_VERSION
RUN \
  echo "**** Install python build dependencies ****" && \
  python3 -m pip install wheel && \
  python3 -m pip install pytest Pillow && \
  echo "**** Start building ****" && \
  export BUILD_DIR="/build_cache" && \
  python3 setup.py bdist_wheel -d dist_musllinux && \
  echo "**** Repairing wheel ****" && \
  PTAG=$(echo $PY_VERSION | tr -d '.' | tr -d '"') && \
  python3 -m pip install auditwheel && \
  python3 -m auditwheel repair -w repaired_dist/ dist_musllinux/*-cp$PTAG-*.whl && \
  echo "**** Testing wheel ****" && \
  python3 -m pip install repaired_dist/*-cp$PTAG-*musllinux*.whl && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  export PH_LIGHT_ACTION=1 && \
  python3 -m pytest && \
  echo "**** Build Done ****"
