# https://github.com/Homebrew/homebrew-core/blob/master/Formula/libheif.rb

class Libheif < Formula
  desc "ISO/IEC 23008-12:2017 HEIF file format decoder and encoder"
  homepage "https://www.libde265.org/"
  url "https://github.com/strukturag/libheif/releases/download/v1.14.0/libheif-1.14.0.tar.gz"
  sha256 "9a2b969d827e162fa9eba582ebd0c9f6891f16e426ef608d089b1f24962295b5"
  license "LGPL-3.0-only"
  # Set current revision from what it was taken plus 10
  revision 10

  depends_on "pkg-config" => :build
  depends_on "jpeg-turbo"
  depends_on "libde265"
  depends_on "libpng"

  def install
    system "./configure", *std_configure_args, "--disable-silent-rules"
    system "make", "install"
  end
end
