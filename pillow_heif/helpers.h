void copy_image_data(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_i16_to_i10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_i16_to_i12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_bgr16_to_rgb10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_bgra16_to_rgba10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgb16_to_rgb10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba16_to_rgba10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_bgr16_to_rgb12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_bgra16_to_rgba12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgb16_to_rgb12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba16_to_rgba12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba16_to_rgba(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba12_to_rgba16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba12_to_bgra16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgb12_to_rgb16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgb12_to_bgr16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba10_to_rgba16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba10_to_bgra16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgb10_to_rgb16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgb10_to_bgr16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba_to_rgba16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba_to_bgra16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgb_to_rgb16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgb_to_bgr16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_bgra_rgba(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_bgr_rgb(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba_premultiplied_to_rgb(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba_premultiplied_to_bgr(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);
