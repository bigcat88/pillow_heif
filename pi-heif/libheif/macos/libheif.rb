# https://github.com/Homebrew/homebrew-core/blob/master/Formula/libheif.rb

class Libheif < Formula
  desc "ISO/IEC 23008-12:2017 HEIF file format decoder and encoder"
  homepage "https://www.libde265.org/"
  url "https://github.com/strukturag/libheif/releases/download/v1.13.0/libheif-1.13.0.tar.gz"
  sha256 "c20ae01bace39e89298f6352f1ff4a54b415b33b9743902da798e8a1e51d7ca1"
  license "LGPL-3.0-only"
  # Set current revision from what it was taken plus 10
  revision 10

  depends_on "pkg-config" => :build
  depends_on "jpeg-turbo"
  depends_on "libde265"
  depends_on "libpng"
  depends_on "shared-mime-info"

  # (001) AOM: remove extend_padding_to_size
  patch do
    url "https://github.com/strukturag/libheif/commit/a01baccaf40bafcabddba47846f5e914ca0724f6.patch"
    sha256 "5ca3b5023891c11a235ef46ae25266c15507387432570544c0ca81d63095d774"
  end

  def install
    system "./configure", *std_configure_args, "--disable-silent-rules"
    system "make", "install"
    pkgshare.install "examples/example.heic"
    pkgshare.install "examples/example.avif"
  end

  def post_install
    system Formula["shared-mime-info"].opt_bin/"update-mime-database", "#{HOMEBREW_PREFIX}/share/mime"
  end
end
