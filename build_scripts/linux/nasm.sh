set -ex \
    && cd /build-tools \
    && NASM_VERSION="2.15.05" \
    && wget https://www.nasm.us/pub/nasm/releasebuilds/${NASM_VERSION}/nasm-${NASM_VERSION}.tar.gz \
    && tar xvf nasm-${NASM_VERSION}.tar.gz \
    && cd nasm-${NASM_VERSION} \
    && ./configure \
    && make -j4 \
    && make install \
    && nasm --version