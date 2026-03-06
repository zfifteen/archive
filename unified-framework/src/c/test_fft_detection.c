#include <stdio.h>
#ifndef __has_include
#  define __has_include(x) 0
#endif
#if __has_include("z5d_fft_zeta.h")
#  define Z5D_HAVE_FFT_ZETA 1
#else
#  define Z5D_HAVE_FFT_ZETA 0
#endif
int main() { printf("Z5D_HAVE_FFT_ZETA=%d\n", Z5D_HAVE_FFT_ZETA); return 0; }
