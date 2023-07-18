ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG PREPARE_CMD
RUN $PREPARE_CMD
ARG INSTALL_CMD
RUN $INSTALL_CMD

COPY . /pillow_heif

ARG EX_ARG
ARG TEST_TYPE

RUN \
    $TEST_TYPE && \
    python3 -m venv --system-site-packages venv && \
    . venv/bin/activate && \
    python3 -m pip install --upgrade pip || echo "pip upgrade failed" && \
    python3 -m pip install --prefer-binary pillow && \
    python3 -m pip install pytest pympler defusedxml && \
    python3 -m pip install --only-binary=:all: numpy || true && \
    python3 -m pip install $EX_ARG --no-deps --only-binary=:all: pillow_heif && \
    \
    python3 -m pytest -v pillow_heif && \
    echo "**** Test Done ****" && \
    python3 -m pip show pillow_heif
