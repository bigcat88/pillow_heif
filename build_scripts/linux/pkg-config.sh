cd /host/build-tools || exit 2
echo "ATTENTION"
echo $(ls -la)
echo "pkg-config-$1"
if [ -d "pkg-config-$1" ]; then
  echo "No cache found for pkg-config, build it..."
  wget --no-check-certificate https://pkg-config.freedesktop.org/releases/pkg-config-"$1".tar.gz \
  && tar xvf pkg-config-"$1".tar.gz \
  && cd pkg-config-"$1" \
  && ./configure --with-internal-glib \
  && make -j4
else
  echo "Cache found for pkg-config, install it..."
  cd "pkg-config-$1"
fi
make install \
&& pkg-config --version