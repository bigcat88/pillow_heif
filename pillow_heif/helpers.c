#ifdef __cplusplus
    extern "C" {
#endif

void copy_image_data(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    if (in_stride == out_stride)
        memcpy(out, in, out_stride * n_rows);
    else
        for (int i = 0; i < n_rows; i++)
            memcpy(out + out_stride * i, in + in_stride * i, out_stride);
}

#ifdef __cplusplus
    }
#endif
