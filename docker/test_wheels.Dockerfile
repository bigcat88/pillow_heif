ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG PREPARE_CMD
RUN $PREPARE_CMD
ARG INSTALL_CMD
RUN $INSTALL_CMD

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --prefer-binary pillow
RUN python3 -m pip install pytest cffi numpy pympler defusedxml

ARG EX_ARG
RUN python3 -m pip install $EX_ARG --no-deps --only-binary=:all: pillow_heif

COPY . /pillow_heif

ARG TEST_TYPE
RUN $TEST_TYPE && \
    python3 -m pytest -rs -v pillow_heif/. && \
    echo "**** Test Done ****" && \
    python3 -m pip show pillow_heif
