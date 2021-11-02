cd /host/build-tools \
&& PKG_CONFIG_VERSION="0.29.2" \
&& wget --no-check-certificate https://pkg-config.freedesktop.org/releases/pkg-config-${PKG_CONFIG_VERSION}.tar.gz \
&& tar xvf pkg-config-${PKG_CONFIG_VERSION}.tar.gz \
&& cd pkg-config-${PKG_CONFIG_VERSION} \
&& ./configure --with-internal-glib \
&& make -j4 \
&& make install \
&& pkg-config --version
