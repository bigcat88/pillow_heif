# https://github.com/Homebrew/homebrew-core/blob/master/Formula/libheif.rb

class Libheif < Formula
  desc "ISO/IEC 23008-12:2017 HEIF file format decoder and encoder"
  homepage "https://www.libde265.org/"
  url "https://github.com/strukturag/libheif/releases/download/v1.12.0/libheif-1.12.0.tar.gz"
  sha256 "e1ac2abb354fdc8ccdca71363ebad7503ad731c84022cf460837f0839e171718"
  license "LGPL-3.0-only"
  # Set current revision from what it was taken plus 10
  revision 12

  depends_on "pkg-config" => :build
  depends_on "aom"
  depends_on "jpeg-turbo"
  depends_on "libde265"
  depends_on "libpng"
  depends_on "shared-mime-info"
  depends_on "x265"

  # Fix -flat_namespace being used on Big Sur and later.
  patch do
    url "https://raw.githubusercontent.com/Homebrew/formula-patches/03cf8088210822aa2c1ab544ed58ea04c897d9c4/libtool/configure-big_sur.diff"
    sha256 "35acd6aebc19843f1a2b3a63e880baceb0f5278ab1ace661e57a502d9d78c93c"
  end

  # Fix loading alpha image
  patch do
    url "https://github.com/strukturag/libheif/commit/4795ba10abd233024d0536096182133fa06d9c3b.patch"
    sha256 "74b6ab5c85307944a292c8044bd8dee4645d413775f8c669b44b63a0cfe81436"
  end

  patch do
    url "https://github.com/strukturag/libheif/commit/c32f15512323960097b99c204535ec53d11fb355.patch"
    sha256 "75ac6e6ca7cecf9bedeb23d21bc60cbc17bf5dcae1c82d39bf388f8d30c6f916"
  end

  # AOM: Fix do not pad minimum to 16x16 pixels
  patch do
    url "https://github.com/strukturag/libheif/commit/ec1dc464dc08517ecef7b675043886ec727eadb2.patch"
    sha256 "0d2a3727e494cb328f5b786d4bb116d167026a86a709219768ab47ed4d2c73c8"
  end

  # AOM: enable lossless
  patch do
    url "https://github.com/strukturag/libheif/commit/b2612dd9c63f8835cf2047960b8cacd464a325a4.patch"
    sha256 "d9747b6191ea142df649166de7cfa4ddb4012530802906c5e0626aed20705325"
  end

  # Fix wrong copy size
  patch do
    url "https://github.com/strukturag/libheif/commit/11ffeffadd980f9f96019fe180fc1e81827e3790.patch"
    sha256 "1a5ea2b0afe73b233daa7a693a9891c0096565f6d72a65a135b05c88e839395a"
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

  test do
    output = "File contains 2 images"
    example = pkgshare/"example.heic"
    exout = testpath/"exampleheic.jpg"

    assert_match output, shell_output("#{bin}/heif-convert #{example} #{exout}")
    assert_predicate testpath/"exampleheic-1.jpg", :exist?
    assert_predicate testpath/"exampleheic-2.jpg", :exist?

    output = "File contains 1 images"
    example = pkgshare/"example.avif"
    exout = testpath/"exampleavif.jpg"

    assert_match output, shell_output("#{bin}/heif-convert #{example} #{exout}")
    assert_predicate testpath/"exampleavif.jpg", :exist?
  end
end
