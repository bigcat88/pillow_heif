cd /host/build-tools \
&& wget --no-check-certificate https://pkg-config.freedesktop.org/releases/pkg-config-"$1".tar.gz \
&& tar xvf pkg-config-"$1".tar.gz \
&& cd pkg-config-"$1" \
&& ./configure --with-internal-glib \
&& make -j4 \
&& make install \
&& pkg-config --version
