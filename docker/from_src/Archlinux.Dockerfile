FROM archlinux:base as base

RUN \
  pacman -Syu --noconfirm && \
  pacman -S --noconfirm python python-pip gcc libheif

FROM base as build_test

COPY . /pillow_heif

RUN \
  cd pillow_heif && \
  python -m venv myenv && \
  source myenv/bin/activate && \
  python3 -m pip install -v ".[tests]"; \
  echo "**** Build Done ****" && \
  python3 -c "import pillow_heif; print(pillow_heif.libheif_info())" && \
  pytest && \
  echo "**** Test Done ****"
