# https://github.com/Homebrew/homebrew-core/blob/master/Formula/libheif.rb

class Libheif < Formula
  desc "ISO/IEC 23008-12:2017 HEIF file format decoder and encoder"
  homepage "https://www.libde265.org/"
  url "https://github.com/strukturag/libheif/releases/download/v1.14.1/libheif-1.14.1.tar.gz"
  sha256 "0634646587454f95e9638ca472a37321aa519fca2ec7405d0e02a74d7ee581db"
  license "LGPL-3.0-only"
  # Set current revision from what it was taken plus 10
  revision 10

  depends_on "pkg-config" => :build
  depends_on "libde265"

  def install
    system "./configure", *std_configure_args, "--disable-silent-rules"
    system "make", "install"
  end
end
