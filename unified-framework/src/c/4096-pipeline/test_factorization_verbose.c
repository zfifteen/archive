#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <openssl/bn.h>
#include <gmp.h>
#include <mpfr.h>

/**
 * Verbose diagnostic for Z5D factorization approach
 *
 * This reveals what the algorithm is actually doing:
 * - Computing theta_prime for modulus N and random primes
 * - Checking if circular distance is within epsilon
 * - Testing division only when geometric filter passes
 */

static mpfr_t phi_mpfr;
static int phi_initialized = 0;

static void ensure_phi_initialized(void) {
    if (phi_initialized) return;
    mpfr_init2(phi_mpfr, 256);
    mpfr_t tmp;
    mpfr_init2(tmp, 256);
    mpfr_sqrt_ui(tmp, 5, MPFR_RNDN);
    mpfr_add_ui(tmp, tmp, 1, MPFR_RNDN);
    mpfr_div_ui(phi_mpfr, tmp, 2, MPFR_RNDN);
    mpfr_clear(tmp);
    phi_initialized = 1;
}

static double theta_prime_from_mpfr(const mpfr_t value, double k) {
    ensure_phi_initialized();
    mpfr_t tmp, k_mp;
    mpfr_init2(tmp, mpfr_get_prec(value));
    mpfr_set(tmp, value, MPFR_RNDN);
    mpfr_div(tmp, tmp, phi_mpfr, MPFR_RNDN);
    mpfr_frac(tmp, tmp, MPFR_RNDN);

    mpfr_init2(k_mp, mpfr_get_prec(value));
    mpfr_set_d(k_mp, k, MPFR_RNDN);
    mpfr_pow(tmp, tmp, k_mp, MPFR_RNDN);
    mpfr_mul(tmp, tmp, phi_mpfr, MPFR_RNDN);
    mpfr_frac(tmp, tmp, MPFR_RNDN);

    double result = mpfr_get_d(tmp, MPFR_RNDN);
    mpfr_clear(k_mp);
    mpfr_clear(tmp);
    return result;
}

static double theta_prime_from_bn(const BIGNUM *bn, double k) {
    char *dec = BN_bn2dec(bn);
    if (!dec) return 0.0;

    mpz_t mpz_value;
    mpz_init_set_str(mpz_value, dec, 10);
    mpfr_t mpfr_value;
    mpfr_init2(mpfr_value, 512);
    mpfr_set_z(mpfr_value, mpz_value, MPFR_RNDN);
    double result = theta_prime_from_mpfr(mpfr_value, k);
    mpfr_clear(mpfr_value);
    mpz_clear(mpz_value);
    OPENSSL_free(dec);
    return result;
}

static double circular_distance(double a, double b) {
    double diff = fmod(a - b + 0.5, 1.0) - 0.5;
    return fabs(diff);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <modulus> [k_param] [epsilon]\n", argv[0]);
        printf("Example: %s 323 0.45 0.3\n", argv[0]);
        return 1;
    }

    const char *modulus_str = argv[1];
    double k = (argc > 2) ? atof(argv[2]) : 0.45;
    double epsilon = (argc > 3) ? atof(argv[3]) : 0.15;

    printf("Z5D Factorization Diagnostic\n");
    printf("=============================\n");
    printf("Modulus N: %s\n", modulus_str);
    printf("K parameter: %.4f\n", k);
    printf("Epsilon threshold: %.4f\n\n", epsilon);

    // Compute theta_N
    mpz_t mpz_N;
    mpz_init_set_str(mpz_N, modulus_str, 10);
    mpfr_t mpfr_N;
    mpfr_init2(mpfr_N, 512);
    mpfr_set_z(mpfr_N, mpz_N, MPFR_RNDN);
    double theta_N = theta_prime_from_mpfr(mpfr_N, k);
    mpfr_clear(mpfr_N);
    mpz_clear(mpz_N);

    printf("theta_N (modulus geometric signature): %.6f\n\n", theta_N);

    // For small modulus 323, compute actual factors
    BN_CTX *ctx = BN_CTX_new();
    BIGNUM *N = BN_new();
    BN_dec2bn(&N, modulus_str);

    printf("Expected factors for N=%s:\n", modulus_str);
    if (strcmp(modulus_str, "323") == 0) {
        printf("  p = 17, q = 19\n");
        BIGNUM *p17 = BN_new();
        BIGNUM *p19 = BN_new();
        BN_set_word(p17, 17);
        BN_set_word(p19, 19);
        double theta_17 = theta_prime_from_bn(p17, k);
        double theta_19 = theta_prime_from_bn(p19, k);
        printf("  theta(17, k=%.2f) = %.6f, distance from N: %.6f\n", k, theta_17, circular_distance(theta_17, theta_N));
        printf("  theta(19, k=%.2f) = %.6f, distance from N: %.6f\n", k, theta_19, circular_distance(theta_19, theta_N));
        printf("  Filter passes: 17=%s, 19=%s\n\n",
               circular_distance(theta_17, theta_N) <= epsilon ? "YES" : "NO",
               circular_distance(theta_19, theta_N) <= epsilon ? "YES" : "NO");
        BN_free(p17);
        BN_free(p19);
    }

    // Now test random primes
    printf("Testing random primes to see filter behavior:\n");
    printf("--------------------------------------------\n");

    int target_bits = BN_num_bits(N) / 2;
    if (target_bits < 8) target_bits = 8;

    BIGNUM *candidate = BN_new();
    int passed_filter = 0;
    int total_tested = 0;

    for (int i = 0; i < 100 && passed_filter < 10; i++) {
        if (!BN_generate_prime_ex(candidate, target_bits, 0, NULL, NULL, NULL)) {
            continue;
        }
        total_tested++;

        double theta_p = theta_prime_from_bn(candidate, k);
        double dist = circular_distance(theta_p, theta_N);

        if (dist <= epsilon) {
            passed_filter++;
            char *p_str = BN_bn2dec(candidate);
            printf("  Prime %d: %s, theta=%.6f, dist=%.6f ✓ PASSES\n",
                   passed_filter, p_str, theta_p, dist);
            OPENSSL_free(p_str);
        }
    }

    printf("\nFilter statistics:\n");
    printf("  Tested: %d random primes\n", total_tested);
    printf("  Passed: %d (%.1f%%)\n", passed_filter, 100.0 * passed_filter / total_tested);
    printf("  Expected pass rate: ~%.1f%% (epsilon=%.2f means ±%.2f circular range)\n\n",
           100.0 * 2 * epsilon, epsilon, epsilon);

    printf("ALGORITHM ANALYSIS:\n");
    printf("-------------------\n");
    printf("The current approach:\n");
    printf("1. Computes theta(N, k) from modulus\n");
    printf("2. Generates RANDOM primes of appropriate bit-size\n");
    printf("3. Filters primes where |theta(p, k) - theta(N, k)| < epsilon\n");
    printf("4. Tests division N %% p == 0\n\n");

    printf("WHY IT FAILS:\n");
    printf("- Random primes are astronomically unlikely to be actual factors\n");
    printf("- Geometric filter reduces search space but doesn't target factors\n");
    printf("- For N=pq, need to find SPECIFIC p or q, not random primes\n");
    printf("- Success probability ≈ (2*epsilon) / (total_primes_in_range)\n\n");

    printf("TO FIX:\n");
    printf("- Need deterministic mapping: theta → candidate prime\n");
    printf("- Or prove theta(p,k) has special relationship to theta(pq,k)\n");
    printf("- Current implementation is essentially trial division with filtering\n");

    BN_free(candidate);
    BN_free(N);
    BN_CTX_free(ctx);

    return 0;
}
