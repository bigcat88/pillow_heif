cd /host/build-tools || exit 2
ls -la
if [[ -d pkg-config-"$1" ]]
then
  echo "No cache found, build it..."
  wget --no-check-certificate https://pkg-config.freedesktop.org/releases/pkg-config-"$1".tar.gz \
  && tar xvf pkg-config-"$1".tar.gz \
  && cd pkg-config-"$1" \
  && ./configure --with-internal-glib \
  && make -j4
else
  echo "Cache found, install it..."
fi
make install \
&& pkg-config --version