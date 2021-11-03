cd /host/build-tools || exit 2
if [[ -d "pkg-config-$1" ]]; then
  echo "Cache found for pkg-config, install it..."
  cd "pkg-config-$1" || exit 102
else
  echo "No cache found for pkg-config, build it..."
  wget -q --no-check-certificate "https://pkg-config.freedesktop.org/releases/pkg-config-$1.tar.gz" \
  && tar xvf "pkg-config-$1.tar.gz" \
  && cd "pkg-config-$1" \
  && ./configure --with-internal-glib \
  && make -j4
fi
make install \
&& pkg-config --version