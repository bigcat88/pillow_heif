set -ex \
    && cd /build-deps \
    && LIBFFI_VERSION="3.3" \
    && wget ftp://sourceware.org/pub/libffi/libffi-${LIBFFI_VERSION}.tar.gz \
    && tar xvf libffi-${LIBFFI_VERSION}.tar.gz \
    && cd libffi-${LIBFFI_VERSION} \
    && ./configure --prefix /usr \
    && make -j4 \
    && make install \
    && ldconfig


cd /host/build-tools || exit 2
if [[ -d "autoconf-$1" ]]; then
  echo "Cache found for autoconf, install it..."
  cd "autoconf-$1" || exit 102
else
  echo "No cache found for autoconf, build it..."
  wget -q --no-check-certificate "https://ftp.gnu.org/gnu/autoconf/autoconf-$1.tar.gz" \
  && tar xvf "autoconf-$1.tar.gz" \
  && cd "autoconf-$1" \
  && ./configure \
  && make -j4
fi
make install \
&& autoconf --version