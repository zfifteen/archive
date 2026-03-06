/Store k estimates as doubles for results structure (note: precision loss for display)/{
N
N
N
N
s/    \/\/ Store k estimates as doubles for results structure (note: precision loss for display)\n    results\.k1_estimate = mpfr_get_d(k1_mpfr, MPFR_RNDN);\n    results\.k2_estimate = mpfr_get_d(k2_mpfr, MPFR_RNDN);\n\n    printf("Factor 1 k estimate: %.2e (index of ~617-digit prime)\\n", results\.k1_estimate);\n    printf("Factor 2 k estimate: %.2e (index of ~617-digit prime)\\n", results\.k2_estimate);/    \/\/ Store k estimates as doubles for results structure\n    results.k1_estimate = mpfr_get_d(k1_mpfr, MPFR_RNDN);\n    results.k2_estimate = mpfr_get_d(k2_mpfr, MPFR_RNDN);\n\n    mpfr_printf("Factor 1 k estimate: %.2Re (index of ~617-digit prime)\\n", k1_mpfr);\n    mpfr_printf("Factor 2 k estimate: %.2Re (index of ~617-digit prime)\\n", k2_mpfr);/
}
