#ifdef __cplusplus
    extern "C" {
#endif

void get_pure_data(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int nRows)
{
    for (int i = 0; i < nRows; i++)
        memcpy(out + out_stride * i,in + in_stride * i , out_stride);
}

#ifdef __cplusplus
    }
#endif
