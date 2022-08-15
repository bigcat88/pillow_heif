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

  # (010) Fix loading alpha image
  patch do
    url "https://github.com/strukturag/libheif/commit/4795ba10abd233024d0536096182133fa06d9c3b.patch"
    sha256 "74b6ab5c85307944a292c8044bd8dee4645d413775f8c669b44b63a0cfe81436"
  end

  # (011)
  patch do
    url "https://github.com/strukturag/libheif/commit/c32f15512323960097b99c204535ec53d11fb355.patch"
    sha256 "75ac6e6ca7cecf9bedeb23d21bc60cbc17bf5dcae1c82d39bf388f8d30c6f916"
  end

  # (012) AOM: Fix do not pad minimum to 16x16 pixels
  patch do
    url "https://github.com/strukturag/libheif/commit/ec1dc464dc08517ecef7b675043886ec727eadb2.patch"
    sha256 "0d2a3727e494cb328f5b786d4bb116d167026a86a709219768ab47ed4d2c73c8"
  end

  # (013) AOM: enable lossless
  patch do
    url "https://github.com/strukturag/libheif/commit/b2612dd9c63f8835cf2047960b8cacd464a325a4.patch"
    sha256 "d9747b6191ea142df649166de7cfa4ddb4012530802906c5e0626aed20705325"
  end

  # (014) Fix RGB(A) to YCbCr chroma position
  patch do
    url "https://github.com/strukturag/libheif/commit/2c8d963dfc0b967e6c78259ba0a99185b27206d8.patch"
    sha256 "5c235e94a6e0ed644942ec9824110800566e750ba9a9a90e92a8d03dd520ae08"
  end

  # (015) Fix RRGGBB to YCbCr chroma position
  patch do
    url "https://github.com/strukturag/libheif/commit/ab0af732fd3c2ebf0211a0a072c76789c8d38d39.patch"
    sha256 "3ba2ae48158b1362edcdd46b8ee56c88f93e540152da7408a429917ccf2bd5bd"
  end

  # (016) Fix RGB to YCbCr chroma sampling position at center(2)
  patch do
    url "https://github.com/strukturag/libheif/commit/2dfc9b2c04ce77c0d85af37a4f66c0ee2dbe058d.patch"
    sha256 "ab9b658197542bcc0d6ed28ebef1879da2b75bcb7ce8d267be90ee998649a523"
  end

  # (017) AVIF: signal chroma sample position when encoding
  patch do
    url "https://github.com/strukturag/libheif/commit/487c3d821df79178edd18a62285449d8d1f70160.patch"
    sha256 "8eda9cf854cd4084a97b8a0c770bf183cc4f567e6a9e1f66288fa27957e26df3"
  end

  # (018) AOM: expose aom decoder errors
  patch do
    url "https://github.com/strukturag/libheif/commit/13c3d59be814a34ceb2ae12da1b6eab3cd85cf72.patch"
    sha256 "9dd1c14838b71b9e593649d36f979c0fea6a85692f591021e06285ec9c392d50"
  end

  # (019) AOM: enable all intra mode by default
  patch do
    url "https://github.com/strukturag/libheif/commit/4ec2ac35e2cd79e8594092f6e36b5eace19cefdf.patch"
    sha256 "98b1074874c5697254f74444a64dd00cfb15ecf5544d873c5c1f2c5cb11b602b"
  end

  # (020) Fix scaling of images
  patch do
    url "https://github.com/strukturag/libheif/commit/0cd461e18b99d018f9adef731eec928781078afb.patch"
    sha256 "81f2c5de8cbd80297208cfd54e95e6f7765c896365ef531ff8f38aaa4f4f6679"
  end

  # (021) Fix overflow of clap box dimensions(1)
  patch do
    url "https://github.com/strukturag/libheif/commit/4193d80e87133b308205d30d234436592fc70c49.diff"
    sha256 "dcb87aa66ea09848e007ce8fed65848b9028b1c7456634d62da690f9c5867195"
  end

  # (022) Fix clap box in supported range(2)
  patch do
    url "https://github.com/strukturag/libheif/commit/ca2473d9eca36697aa531f42209567cc663ceaee.patch"
    sha256 "e6f107c77c8b8ffc00e12d37a11a29642b5db2aadd552fa7d7033c4368c689f2"
  end

  # (023) Clap box sizes to unsigned(3)
  patch do
    url "https://github.com/strukturag/libheif/commit/2c4cb5712724b5617019dc749b91b0acd0f9ad7c.patch"
    sha256 "a6fde7081abe1fd5d3b9bc4e850cdbb16790d2105971111c86657696bad39438"
  end

  # (024) Fix AVIF left shift undefined behaviour
  patch do
    url "https://github.com/strukturag/libheif/commit/82070385eca01f64c587e02c0a75d60386d308c3.patch"
    sha256 "64d51a24cb26af69fbca98c8394cd1682b0d16eb9a50412635a20ee153e3372b"
  end

  # (025) Fix bitstream potential overflow
  patch do
    url "https://github.com/strukturag/libheif/commit/67410c3ce2c8a210d42d02c790c3ac1f9791605a.patch"
    sha256 "368a8965118647a8e7ca6e9b454cac94b72f3b26711bfd3d371e274b59b94007"
  end

  # (026) Fix encoder when no SPS returned(1)
  patch do
    url "https://github.com/strukturag/libheif/commit/2611d39704bdb6bb37429e39660d9dedbdfff35a.patch"
    sha256 "7cbca7d0f8f6743d0997a3b5102a1397eb967261e96c8946ad70e195d93cc24f"
  end

  # (027) Fix checking result of `read`
  patch do
    url "https://github.com/strukturag/libheif/commit/5a20339c29831cd2f72903a1ca2ff88e458dc1c2.patch"
    sha256 "a07fc8974cf1f0634c158c72ac6c3263457c6d91a0e66143607c9ee2fcb72feb"
  end

  # (028) Fix encoder when no SPS returned(2)
  patch do
    url "https://github.com/strukturag/libheif/commit/98b867ea575ecce7039458b71f2c320742489e30.patch"
    sha256 "1e063aef2a871526e99247615d439bc7055034e443d5537d6702db09a470a9f9"
  end

  # (029) NCLX: avoid division by zero
  patch do
    url "https://github.com/strukturag/libheif/commit/9497e10168660138fd10a738179039c0e7d7ba6c.patch"
    sha256 "97fc5e57727d9ea47aa7dbdf2635afd40122ca1a0f9d44be228d3d14efd7c610"
  end

  # (030) Fix wrong copy size
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
