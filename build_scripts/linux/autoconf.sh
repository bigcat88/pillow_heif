cd /host/build-tools || exit 2
if [[ -d "autoconf-$1" ]]; then
  echo "Cache found for autoconf, install it..."
  cd "autoconf-$1" || exit 102
else
  echo "No cache found for autoconf, build it..."
  wget --no-check-certificate "https://ftp.gnu.org/gnu/autoconf/autoconf-$1.tar.gz" \
  && tar xvf "autoconf-$1.tar.gz" \
  && cd "autoconf-$1" \
  && ./configure \
  && make -j4
fi
make install \
&& autoconf --version