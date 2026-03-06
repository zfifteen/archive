#include "z5d_predictor.h"
#include <time.h>
int main(void) {
    printf("Z5D Performance Benchmark\n");
    printf("========================\n");
    clock_t start = clock();
    for (int i = 0; i < 100000; i++) {
        z5d_prime(1000 + i, 0.0, 0.0, 0.3, 1);
    }
    clock_t end = clock();
    double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("100,000 predictions in %.3f seconds\n", elapsed);
    printf("Average: %.2f μs per prediction\n", elapsed / 100000.0 * 1000000.0);
    return 0;
}
