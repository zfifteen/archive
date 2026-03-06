#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <stdint.h>

#include "../lis_corrector/lis_corrector.h"

static void usage(const char* prog) {
    fprintf(stderr, "Usage: %s <n> [--window W]\n", prog);
}

static uint64_t fixed_window_for_n(uint64_t n) {
    if (n >= 1000 && n <= 10000) return 5000;
    if (n > 10000 && n <= 100000) return 5000;
    if (n > 100000 && n <= 1000000) return 10000;
    if (n > 1000000 && n <= 10000000) return 100000;
    if (n > 10000000 && n <= 100000000) return 1000000;
    fprintf(stderr, "Error: n=%" PRIu64 " out of supported bands (1e3..1e8).\n", n);
    exit(2);
}

int main(int argc, char** argv) {
    if (argc < 2) { usage(argv[0]); return 1; }
    uint64_t n = 0;
    uint64_t window = 0;

    n = strtoull(argv[1], NULL, 10);
    if (n == 0) { usage(argv[0]); return 1; }

    for (int i = 2; i < argc; ++i) {
        if (strcmp(argv[i], "--window") == 0 && i + 1 < argc) {
            window = strtoull(argv[++i], NULL, 10);
        }
    }
    if (window == 0) window = fixed_window_for_n(n);

    uint64_t p_true=0, mr_calls=0, baseline=0;
    int rc = lis_correct_nth_prime(n, window, &p_true, &mr_calls, &baseline);
    if (rc != 0) {
        fprintf(stderr, "lis_correct_nth_prime failed (rc=%d) for n=%" PRIu64 " with window=%" PRIu64 "\n", rc, n, window);
        return rc;
    }
    double reduction = 0.0;
    if (baseline > 0) reduction = 100.0 * (1.0 - ((double)mr_calls / (double)baseline));
    printf("n,prime,baseline,mr_calls,reduction_pct\n");
    printf("%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%.2f\n", n, p_true, baseline, mr_calls, reduction);
    return 0;
}

