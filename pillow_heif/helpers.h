void copy_image_data(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows);

void convert_rgba_to_rgba16(const uint8_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements);

void convert_rgba_to_bgra16(const uint8_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements);

void convert_rgb_to_rgb16(const uint8_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements);

void convert_rgb_to_bgr16(const uint8_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements);

void convert_bgra_rgba(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows, int stride_elements);

void convert_bgr_rgb(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows, int stride_elements);
