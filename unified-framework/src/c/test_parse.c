#include <mpfr.h>
#include <stdio.h>

int main() {
    mpfr_t x;
    mpfr_init2(x, 128);
    
    printf("Testing mpfr_set_str with '1e100':\n");
    int ret = mpfr_set_str(x, "1e100", 0, MPFR_RNDN);
    printf("Return code: %d\n", ret);
    printf("Value: ");
    mpfr_printf("%.Rg\n", x);
    
    mpfr_clear(x);
    return 0;
}
