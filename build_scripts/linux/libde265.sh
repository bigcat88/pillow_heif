set -ex \
    && cd /build-deps \
    && LIBDE265_VERSION="1.0.8" \
    && wget https://github.com/strukturag/libde265/releases/download/v${LIBDE265_VERSION}/libde265-${LIBDE265_VERSION}.tar.gz \
    && tar xvf libde265-${LIBDE265_VERSION}.tar.gz \
    && cd libde265-${LIBDE265_VERSION} \
    && ./autogen.sh \
    && ./configure --disable-dec265 --disable-sherlock265 --prefix /usr \
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