/**
 * AMX Lucas-Lehmer Smoke Test
 * ===========================
 *
 * Simple standalone test of AMX-accelerated 2x2 matrix exponentiation
 * for Lucas-Lehmer sequence optimization.
 *
 * Concept: S_n = [4, 1] * M^n * [1; 0] where M = [[4, -2], [1, 0]]
 * This should give massive speedup for large p values.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <gmp.h>

// AMX macros from z-amx research
#ifdef __aarch64__
#define AMX_NOP_OP_IMM5(op, imm5) \
    __asm("nop\nnop\nnop\n.word (0x201000 + (%0 << 5) + %1)" : : "i"(op), "i"(imm5) : "memory")

#define AMX_OP_GPR(op, gpr) \
    __asm(".word (0x201000 + (%0 << 5) + 0%1 - ((0%1 >> 4) * 6))" : : "i"(op), "r"((uint64_t)(gpr)) : "memory")

#define AMX_SET()       AMX_NOP_OP_IMM5(17, 0)
#define AMX_CLR()       AMX_NOP_OP_IMM5(17, 1)
#define AMX_MATINT(gpr) AMX_OP_GPR(20, gpr)
#define AMX_LDX(gpr)    AMX_OP_GPR(0, gpr)
#define AMX_LDY(gpr)    AMX_OP_GPR(1, gpr)
#define AMX_STZ(gpr)    AMX_OP_GPR(5, gpr)

#define HAS_AMX 1
#else
#define HAS_AMX 0
#define AMX_SET()
#define AMX_CLR()
#endif

// 2x2 matrix for Lucas-Lehmer transformation
typedef struct {
    uint32_t m[4];  // [[m[0], m[1]], [m[2], m[3]]]
} matrix2x2_t;

// Standard matrix multiply (no AMX)
void matrix_mult_standard(matrix2x2_t *result, const matrix2x2_t *a, const matrix2x2_t *b, const mpz_t mod) {
    mpz_t temp, sum;
    mpz_init(temp);
    mpz_init(sum);

    // result[0][0] = (a[0][0] * b[0][0] + a[0][1] * b[1][0]) % mod
    mpz_set_ui(sum, a->m[0]);
    mpz_mul_ui(sum, sum, b->m[0]);
    mpz_set_ui(temp, a->m[1]);
    mpz_mul_ui(temp, temp, b->m[2]);
    mpz_add(sum, sum, temp);
    mpz_mod(sum, sum, mod);
    result->m[0] = mpz_get_ui(sum);

    // result[0][1] = (a[0][0] * b[0][1] + a[0][1] * b[1][1]) % mod
    mpz_set_ui(sum, a->m[0]);
    mpz_mul_ui(sum, sum, b->m[1]);
    mpz_set_ui(temp, a->m[1]);
    mpz_mul_ui(temp, temp, b->m[3]);
    mpz_add(sum, sum, temp);
    mpz_mod(sum, sum, mod);
    result->m[1] = mpz_get_ui(sum);

    // result[1][0] = (a[1][0] * b[0][0] + a[1][1] * b[1][0]) % mod
    mpz_set_ui(sum, a->m[2]);
    mpz_mul_ui(sum, sum, b->m[0]);
    mpz_set_ui(temp, a->m[3]);
    mpz_mul_ui(temp, temp, b->m[2]);
    mpz_add(sum, sum, temp);
    mpz_mod(sum, sum, mod);
    result->m[2] = mpz_get_ui(sum);

    // result[1][1] = (a[1][0] * b[0][1] + a[1][1] * b[1][1]) % mod
    mpz_set_ui(sum, a->m[2]);
    mpz_mul_ui(sum, sum, b->m[1]);
    mpz_set_ui(temp, a->m[3]);
    mpz_mul_ui(temp, temp, b->m[3]);
    mpz_add(sum, sum, temp);
    mpz_mod(sum, sum, mod);
    result->m[3] = mpz_get_ui(sum);

    mpz_clear(temp);
    mpz_clear(sum);
}

#ifdef __aarch64__
// AMX-accelerated matrix multiply (proof of concept)
void matrix_mult_amx(matrix2x2_t *result, const matrix2x2_t *a, const matrix2x2_t *b, const mpz_t mod) {
    // For smoke test, use AMX instructions but fall back to standard math
    // In production, this would use full AMX matrix operations
    AMX_SET();

    // AMX operations would go here - for now, use standard math with AMX overhead
    matrix_mult_standard(result, a, b, mod);

    AMX_CLR();
}
#else
void matrix_mult_amx(matrix2x2_t *result, const matrix2x2_t *a, const matrix2x2_t *b, const mpz_t mod) {
    matrix_mult_standard(result, a, b, mod);
}
#endif

// Matrix exponentiation using binary method
void matrix_power(matrix2x2_t *result, const matrix2x2_t *base, uint32_t exp, const mpz_t mod, int use_amx) {
    // Initialize result as identity matrix
    result->m[0] = 1; result->m[1] = 0;
    result->m[2] = 0; result->m[3] = 1;

    matrix2x2_t base_copy = *base;
    matrix2x2_t temp;

    while (exp > 0) {
        if (exp & 1) {
            // result = result * base_copy
            if (use_amx) {
                matrix_mult_amx(&temp, result, &base_copy, mod);
            } else {
                matrix_mult_standard(&temp, result, &base_copy, mod);
            }
            *result = temp;
        }

        // base_copy = base_copy * base_copy
        if (use_amx) {
            matrix_mult_amx(&temp, &base_copy, &base_copy, mod);
        } else {
            matrix_mult_standard(&temp, &base_copy, &base_copy, mod);
        }
        base_copy = temp;

        exp >>= 1;
    }
}

// Lucas-Lehmer test using matrix exponentiation
int lucas_lehmer_matrix(uint32_t p, int use_amx) {
    if (p == 2) return 1;  // 2^2 - 1 = 3 is prime
    if (p < 3) return 0;

    mpz_t mersenne;
    mpz_init(mersenne);

    // Calculate 2^p - 1
    mpz_ui_pow_ui(mersenne, 2, p);
    mpz_sub_ui(mersenne, mersenne, 1);

    // Lucas-Lehmer transformation matrix: [[4, -2], [1, 0]]
    matrix2x2_t transform;
    transform.m[0] = 4; transform.m[1] = (uint32_t)(-2);  // Will be handled in modular arithmetic
    transform.m[2] = 1; transform.m[3] = 0;

    // Compute transform^(p-2)
    matrix2x2_t result;
    matrix_power(&result, &transform, p - 2, mersenne, use_amx);

    // Apply to initial vector [4, 1]: result_vector = result * [4; 1]
    mpz_t final_val, temp;
    mpz_init(final_val);
    mpz_init(temp);

    // final_val = result[0][0] * 4 + result[0][1] * 1
    mpz_set_ui(final_val, result.m[0]);
    mpz_mul_ui(final_val, final_val, 4);
    mpz_set_ui(temp, result.m[1]);
    mpz_add(final_val, final_val, temp);
    mpz_mod(final_val, final_val, mersenne);

    int is_prime = (mpz_cmp_ui(final_val, 0) == 0);

    mpz_clear(mersenne);
    mpz_clear(final_val);
    mpz_clear(temp);

    return is_prime;
}

// Standard Lucas-Lehmer for comparison
int lucas_lehmer_standard(uint32_t p) {
    if (p == 2) return 1;
    if (p < 3) return 0;

    mpz_t mersenne, s, temp;
    mpz_init(mersenne);
    mpz_init(s);
    mpz_init(temp);

    // Calculate 2^p - 1
    mpz_ui_pow_ui(mersenne, 2, p);
    mpz_sub_ui(mersenne, mersenne, 1);

    // Initialize S_0 = 4
    mpz_set_ui(s, 4);

    // Iterate p-2 times: S_{i+1} = S_i^2 - 2 (mod mersenne)
    for (uint32_t i = 0; i < p - 2; i++) {
        mpz_mul(temp, s, s);
        mpz_sub_ui(temp, temp, 2);
        mpz_mod(s, temp, mersenne);
    }

    int is_prime = (mpz_cmp_ui(s, 0) == 0);

    mpz_clear(mersenne);
    mpz_clear(s);
    mpz_clear(temp);

    return is_prime;
}

int main() {
    printf("AMX Lucas-Lehmer Smoke Test\n");
    printf("===========================\n");
    printf("AMX Available: %s\n", HAS_AMX ? "YES" : "NO");
    printf("\n");

    // Test cases: known results
    uint32_t test_cases[] = {3, 5, 7, 13, 17, 19, 11, 23};  // Mix of primes and composites
    int expected[] = {1, 1, 1, 1, 1, 1, 0, 0};  // 2^p-1 primality
    int num_tests = sizeof(test_cases) / sizeof(test_cases[0]);

    printf("Testing small cases:\n");
    for (int i = 0; i < num_tests; i++) {
        uint32_t p = test_cases[i];

        clock_t start = clock();
        int standard_result = lucas_lehmer_standard(p);
        clock_t mid = clock();
        int matrix_result = lucas_lehmer_matrix(p, 0);
        clock_t matrix_end = clock();
        int amx_result = lucas_lehmer_matrix(p, 1);
        clock_t end = clock();

        double standard_time = (double)(mid - start) / CLOCKS_PER_SEC * 1000;
        double matrix_time = (double)(matrix_end - mid) / CLOCKS_PER_SEC * 1000;
        double amx_time = (double)(end - matrix_end) / CLOCKS_PER_SEC * 1000;

        printf("p=%2d: Standard=%d Matrix=%d AMX=%d Expected=%d ",
               p, standard_result, matrix_result, amx_result, expected[i]);

        if (standard_result == expected[i] && matrix_result == expected[i] && amx_result == expected[i]) {
            printf("✅ PASS");
        } else {
            printf("❌ FAIL");
        }

        printf(" (%.2f/%.2f/%.2f ms)\n", standard_time, matrix_time, amx_time);
    }

    printf("\nSMOKE TEST COMPLETE\n");
    return 0;
}