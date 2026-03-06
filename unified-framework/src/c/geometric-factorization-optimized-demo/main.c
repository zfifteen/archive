#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <mpfr.h>
#include <gmp.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>
#include <sys/time.h>
#include "../z_framework_params.h"
#include "../z5d_predictor.h"
#include "../4096-pipeline/z_seed_generator.h"
#include "golden_spiral.h"

// Constants
#define MPFR_PRECISION 64
#define PHI 1.618033988749895
#define MAX_CANDIDATES 10000
#define MAX_SEMIPRIMES 1000
#define MR_GEODESIC_WITNESSES 6
#define MR_STANDARD_WITNESSES 8

static const unsigned long MR_STANDARD_BASES[MR_STANDARD_WITNESSES] = {
    2UL, 3UL, 5UL, 7UL, 11UL, 13UL, 17UL, 19UL
};

// Configuration structure
typedef struct {
    uint8_t seed[SEED_SIZE];
    char seed_hex[HEX_SEED_LEN];
    double kappa_geo;
    double kappa_star;
    int bump_p;
    int bump_q;
} config_t;

// Miller-Rabin context
typedef struct {
    mpz_t n;
    mpz_t n_minus_1;
    mpz_t n_minus_3;
    mpz_t d;
    unsigned long r;
} mr_context_t;

// Global variables
mpfr_t mpfr_phi, temp1, temp2, temp3;

// Function prototypes
void init_mpfr();
void cleanup_mpfr();
double compute_geometric_coordinate(mpfr_t n, double k);
double circ_dist(double a, double b);
int is_prime(mpz_t n);
int generate_candidates(mpz_t candidates[], mpfr_t N_mpfr, double k, double eps);
int geometric_factorize(mpz_t N, mpfr_t N_mpfr, double k, double eps, mpz_t p_out, mpz_t q_out);
int multi_pass_factorize(mpz_t N, mpfr_t N_mpfr, mpz_t p_out, mpz_t q_out);
void generate_semiprimes(mpz_t semiprimes_N[], mpz_t semiprimes_p[], mpz_t semiprimes_q[], int *count, int samples, int bit_size, unsigned int seed);

// Z5D helper functions
static int init_config(config_t *cfg);
static void derive_seed(const uint8_t *base_seed, const char *tag, unsigned char *output, size_t output_size);
static void mr_context_init(mr_context_t *ctx, const mpz_t n);
static void mr_context_clear(mr_context_t *ctx);
static void map_witness_into_range(const mr_context_t *ctx, mpz_t witness);
static void generate_standard_witnesses(mpz_t *witnesses, size_t count, const mr_context_t *ctx);
static void generate_geodesic_witnesses(mpz_t *witnesses, size_t count, const mpz_t candidate, const config_t *cfg, unsigned long hint, const mr_context_t *ctx);
static int miller_rabin_round(const mr_context_t *ctx, const mpz_t witness);
static int candidate_is_probable_prime(const mpz_t candidate, const config_t *cfg, unsigned long hint);
static void z5d_prime_count(const mpz_t x, mpz_t count_out, const config_t *cfg);
static int z5d_nth_prime(const char *label, const mpz_t k, mpz_t prime_out, const config_t *cfg, const mpz_t *too_close_ref, int enforce_not_too_close);
static void seed_to_2048bit(const unsigned char *seed_bytes, mpz_t result);

// Implementation of Z5D functions
static int init_config(config_t *cfg) {
    int rc = z_generate_seed(cfg->seed);
    if (rc != ZSEED_OK) {
        return rc;
    }
    z_seed_to_hex(cfg->seed, cfg->seed_hex);
    cfg->kappa_geo = ZF_KAPPA_GEO_DEFAULT;
    cfg->kappa_star = ZF_KAPPA_STAR_DEFAULT;
    cfg->bump_p = 0;
    cfg->bump_q = 1;
    return ZSEED_OK;
}

static void derive_seed(const uint8_t *base_seed, const char *tag, unsigned char *output, size_t output_size) {
    const size_t TAG_PREFIX_MAX = 32;
    unsigned char context[SEED_SIZE + TAG_PREFIX_MAX];
    unsigned char digest[SHA256_DIGEST_LENGTH];

    if (!output || output_size == 0) {
        return;
    }

    if (!base_seed || !tag) {
        memset(output, 0, output_size);
        return;
    }

    memset(context, 0, sizeof(context));
    size_t tag_len = strlen(tag);
    if (tag_len > TAG_PREFIX_MAX) {
        tag_len = TAG_PREFIX_MAX;
    }
    memcpy(context, tag, tag_len);
    memcpy(context + tag_len, base_seed, SEED_SIZE);

    SHA256(context, tag_len + SEED_SIZE, digest);

    size_t produced = 0;
    while (produced < output_size) {
        size_t chunk = SHA256_DIGEST_LENGTH;
        if (chunk > output_size - produced) {
            chunk = output_size - produced;
        }
        memcpy(output + produced, digest, chunk);
        produced += chunk;
        if (produced < output_size) {
            SHA256(digest, SHA256_DIGEST_LENGTH, digest);
        }
    }
    OPENSSL_cleanse(context, sizeof(context));
    OPENSSL_cleanse(digest, sizeof(digest));
}

static void mr_context_init(mr_context_t *ctx, const mpz_t n) {
    mpz_init_set(ctx->n, n);
    mpz_init(ctx->n_minus_1);
    mpz_sub_ui(ctx->n_minus_1, ctx->n, 1);
    mpz_init(ctx->n_minus_3);
    if (mpz_cmp_ui(ctx->n, 3) > 0) {
        mpz_sub_ui(ctx->n_minus_3, ctx->n, 3);
    } else {
        mpz_set_ui(ctx->n_minus_3, 0);
    }
    mpz_init_set(ctx->d, ctx->n_minus_1);
    ctx->r = 0;
    while (mpz_even_p(ctx->d)) {
        mpz_fdiv_q_2exp(ctx->d, ctx->d, 1);
        ctx->r++;
    }
}

static void mr_context_clear(mr_context_t *ctx) {
    mpz_clear(ctx->n);
    mpz_clear(ctx->n_minus_1);
    mpz_clear(ctx->n_minus_3);
    mpz_clear(ctx->d);
}

static void map_witness_into_range(const mr_context_t *ctx, mpz_t witness) {
    if (mpz_cmp_ui(witness, 2) < 0) {
        mpz_set_ui(witness, 2);
        return;
    }

    if (mpz_cmp(witness, ctx->n_minus_1) >= 0) {
        if (mpz_cmp_ui(ctx->n_minus_3, 1) <= 0) {
            mpz_set_ui(witness, 2);
        } else {
            mpz_mod(witness, witness, ctx->n_minus_3);
            mpz_add_ui(witness, witness, 2);
        }
    }
}

static void generate_standard_witnesses(mpz_t *witnesses, size_t count, const mr_context_t *ctx) {
    size_t limit = count < MR_STANDARD_WITNESSES ? count : MR_STANDARD_WITNESSES;
    for (size_t i = 0; i < limit; ++i) {
        mpz_set_ui(witnesses[i], MR_STANDARD_BASES[i]);
        map_witness_into_range(ctx, witnesses[i]);
    }
}

static void generate_geodesic_witnesses(mpz_t *witnesses, size_t count, const mpz_t candidate, const config_t *cfg, unsigned long hint, const mr_context_t *ctx) {
    if (count == 0) {
        return;
    }

    if (mpz_cmp_ui(ctx->n_minus_3, 1) <= 0) {
        for (size_t i = 0; i < count; ++i) {
            mpz_set_ui(witnesses[i], 2);
        }
        return;
    }

    size_t buf_size = (mpz_sizeinbase(candidate, 2) + 7) / 8;
    if (buf_size == 0) {
        buf_size = 1;
    }

    unsigned char *candidate_bytes = (unsigned char*)malloc(buf_size);
    if (!candidate_bytes) {
        for (size_t i = 0; i < count; ++i) {
            mpz_set_ui(witnesses[i], 2);
        }
        return;
    }

    size_t exported = 0;
    mpz_export(candidate_bytes, &exported, 1, 1, 0, 0, candidate);
    if (exported == 0) {
        exported = 1;
        candidate_bytes[0] = 0;
    }

    for (size_t i = 0; i < count; ++i) {
        unsigned char digest[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha_ctx;
        SHA256_Init(&sha_ctx);
        SHA256_Update(&sha_ctx, candidate_bytes, exported);
        if (cfg) {
            SHA256_Update(&sha_ctx, cfg->seed, SEED_SIZE);
        }
        SHA256_Update(&sha_ctx, &hint, sizeof(hint));
        SHA256_Update(&sha_ctx, &i, sizeof(i));
        SHA256_Final(digest, &sha_ctx);

        mpz_import(witnesses[i], SHA256_DIGEST_LENGTH, 1, 1, 0, 0, digest);
        map_witness_into_range(ctx, witnesses[i]);
    }

    OPENSSL_cleanse(candidate_bytes, buf_size);
    free(candidate_bytes);
}

static int miller_rabin_round(const mr_context_t *ctx, const mpz_t witness) {
    mpz_t x;
    mpz_init(x);

    mpz_powm(x, witness, ctx->d, ctx->n);
    if (mpz_cmp_ui(x, 1) == 0 || mpz_cmp(x, ctx->n_minus_1) == 0) {
        mpz_clear(x);
        return 1;
    }

    for (unsigned long i = 1; i < ctx->r; ++i) {
        mpz_powm_ui(x, x, 2, ctx->n);
        if (mpz_cmp(x, ctx->n_minus_1) == 0) {
            mpz_clear(x);
            return 1;
        }
    }

    mpz_clear(x);
    return 0;
}

static int candidate_is_probable_prime(const mpz_t candidate, const config_t *cfg, unsigned long hint) {
    if (mpz_cmp_ui(candidate, 2) < 0) {
        return 0;
    }
    if (mpz_cmp_ui(candidate, 2) == 0) {
        return 1;
    }
    if (mpz_even_p(candidate)) {
        return 0;
    }

    mr_context_t ctx;
    mr_context_init(&ctx, candidate);

    mpz_t geodesic[MR_GEODESIC_WITNESSES];
    mpz_t standard[MR_STANDARD_WITNESSES];

    for (size_t i = 0; i < MR_GEODESIC_WITNESSES; ++i) {
        mpz_init(geodesic[i]);
    }
    for (size_t i = 0; i < MR_STANDARD_WITNESSES; ++i) {
        mpz_init(standard[i]);
    }

    generate_geodesic_witnesses(geodesic, MR_GEODESIC_WITNESSES, candidate, cfg, hint, &ctx);
    generate_standard_witnesses(standard, MR_STANDARD_WITNESSES, &ctx);

    for (size_t i = 0; i < MR_GEODESIC_WITNESSES; ++i) {
        if (!miller_rabin_round(&ctx, geodesic[i])) {
            for (size_t j = 0; j < MR_GEODESIC_WITNESSES; ++j) {
                mpz_clear(geodesic[j]);
            }
            for (size_t j = 0; j < MR_STANDARD_WITNESSES; ++j) {
                mpz_clear(standard[j]);
            }
            mr_context_clear(&ctx);
            return 0;
        }
    }

    for (size_t i = 0; i < MR_STANDARD_WITNESSES; ++i) {
        if (!miller_rabin_round(&ctx, standard[i])) {
            for (size_t j = 0; j < MR_GEODESIC_WITNESSES; ++j) {
                mpz_clear(geodesic[j]);
            }
            for (size_t j = 0; j < MR_STANDARD_WITNESSES; ++j) {
                mpz_clear(standard[j]);
            }
            mr_context_clear(&ctx);
            return 0;
        }
    }

    for (size_t i = 0; i < MR_GEODESIC_WITNESSES; ++i) {
        mpz_clear(geodesic[i]);
    }
    for (size_t i = 0; i < MR_STANDARD_WITNESSES; ++i) {
        mpz_clear(standard[i]);
    }
    mr_context_clear(&ctx);
    return 1;
}

static void z5d_prime_count(const mpz_t x, mpz_t count_out, const config_t *cfg) {
    if (mpz_cmp_ui(x, 2) < 0) {
        mpz_set_ui(count_out, 0);
        return;
    }

    int precision_bits = mpz_sizeinbase(x, 2) + 64;
    if (precision_bits < 256) {
        precision_bits = 256;
    }

    mpfr_t x_mpfr, ln_x, pnt_base, z5d_correction, result;
    mpfr_init2(x_mpfr, precision_bits);
    mpfr_init2(ln_x, precision_bits);
    mpfr_init2(pnt_base, precision_bits);
    mpfr_init2(z5d_correction, precision_bits);
    mpfr_init2(result, precision_bits);

    mpfr_set_z(x_mpfr, x, MPFR_RNDN);
    mpfr_log(ln_x, x_mpfr, MPFR_RNDN);

    mpfr_div(pnt_base, x_mpfr, ln_x, MPFR_RNDN);

    mpfr_t temp1, temp2, kappa_star_mpfr, c_calibrated_mpfr;
    mpfr_init2(temp1, precision_bits);
    mpfr_init2(temp2, precision_bits);
    mpfr_init2(kappa_star_mpfr, precision_bits);
    mpfr_init2(c_calibrated_mpfr, precision_bits);

    double kappa_star = cfg ? cfg->kappa_star : ZF_KAPPA_STAR_DEFAULT;
    mpfr_set_d(kappa_star_mpfr, kappa_star, MPFR_RNDN);
    mpfr_set_d(c_calibrated_mpfr, ZF_Z5D_C_CALIBRATED, MPFR_RNDN);

    mpfr_mul(temp1, kappa_star_mpfr, ln_x, MPFR_RNDN);
    mpfr_add(temp2, temp1, c_calibrated_mpfr, MPFR_RNDN);
    mpfr_add_ui(z5d_correction, temp2, 1, MPFR_RNDN);

    mpfr_mul(result, pnt_base, z5d_correction, MPFR_RNDN);

    mpfr_get_z(count_out, result, MPFR_RNDN);

    mpfr_clear(x_mpfr);
    mpfr_clear(ln_x);
    mpfr_clear(pnt_base);
    mpfr_clear(z5d_correction);
    mpfr_clear(result);
    mpfr_clear(temp1);
    mpfr_clear(temp2);
    mpfr_clear(kappa_star_mpfr);
    mpfr_clear(c_calibrated_mpfr);
}

static void seed_to_2048bit(const unsigned char *seed_bytes, mpz_t result) {
    unsigned char expanded[256];
    derive_seed(seed_bytes, "2048bit", expanded, sizeof(expanded));

    mpz_import(result, sizeof(expanded), 1, 1, 0, 0, expanded);

    mpz_setbit(result, 2047);
    mpz_setbit(result, 0);
}

// Helper function for too_close (from key_gen)
static inline int x931_too_close_2048(const mpz_t a, const mpz_t b) {
    mpz_t ah, bh;
    mpz_inits(ah, bh, NULL);
    mpz_fdiv_q_2exp(ah, a, 2048 - 100);
    mpz_fdiv_q_2exp(bh, b, 2048 - 100);
    int eq = (mpz_cmp(ah, bh) == 0);
    mpz_clears(ah, bh, NULL);
    return eq;
}

static int z5d_nth_prime(const char *label, const mpz_t k, mpz_t prime_out, const config_t *cfg, const mpz_t *too_close_ref, int enforce_not_too_close) {
    if (mpz_cmp_d(k, ZF_MIN_K_NTH) >= 0) {
        int precision_bits = mpz_sizeinbase(k, 2) + 128;
        if (precision_bits < 256) {
            precision_bits = 256;
        }

        mpfr_t k_mpfr, ln_k, ln_ln_k, z5d_estimate;
        mpfr_init2(k_mpfr, precision_bits);
        mpfr_init2(ln_k, precision_bits);
        mpfr_init2(ln_ln_k, precision_bits);
        mpfr_init2(z5d_estimate, precision_bits);

        mpfr_set_z(k_mpfr, k, MPFR_RNDN);
        mpfr_log(ln_k, k_mpfr, MPFR_RNDN);
        mpfr_log(ln_ln_k, ln_k, MPFR_RNDN);

        mpfr_t correction_term, kappa_star_mpfr, temp;
        mpfr_init2(correction_term, precision_bits);
        mpfr_init2(kappa_star_mpfr, precision_bits);
        mpfr_init2(temp, precision_bits);

        double kappa_star = cfg ? cfg->kappa_star : ZF_KAPPA_STAR_DEFAULT;
        mpfr_set_d(kappa_star_mpfr, kappa_star, MPFR_RNDN);

        mpfr_div(temp, ln_ln_k, ln_k, MPFR_RNDN);
        mpfr_mul(correction_term, kappa_star_mpfr, temp, MPFR_RNDN);

        mpfr_add(temp, ln_k, ln_ln_k, MPFR_RNDN);
        mpfr_sub_ui(temp, temp, 1, MPFR_RNDN);
        mpfr_add(temp, temp, correction_term, MPFR_RNDN);
        mpfr_mul(z5d_estimate, k_mpfr, temp, MPFR_RNDN);

        mpz_t estimated_prime;
        mpz_init(estimated_prime);
        mpfr_get_z(estimated_prime, z5d_estimate, MPFR_RNDN);

        if (mpz_cmp(estimated_prime, k) < 0) {
            mpz_mul_ui(estimated_prime, k, 10);
        }

        mpz_set(prime_out, estimated_prime);
        if (mpz_even_p(prime_out)) {
            mpz_add_ui(prime_out, prime_out, 1);
        }

        const unsigned long MAX_LOCAL_ATTEMPTS = 100UL;

        // Simple search for prime near estimate
        for (unsigned long attempt = 0; attempt < MAX_LOCAL_ATTEMPTS; ++attempt) {
            if (candidate_is_probable_prime(prime_out, cfg, 0)) {
                if (!enforce_not_too_close || !too_close_ref ||
                    !x931_too_close_2048((*too_close_ref), prime_out)) {
                    mpfr_clear(k_mpfr);
                    mpfr_clear(ln_k);
                    mpfr_clear(ln_ln_k);
                    mpfr_clear(z5d_estimate);
                    mpfr_clear(correction_term);
                    mpfr_clear(kappa_star_mpfr);
                    mpfr_clear(temp);
                    mpz_clear(estimated_prime);
                    return 1;
                }
            }
            mpz_add_ui(prime_out, prime_out, 2);
        }

        mpfr_clear(k_mpfr);
        mpfr_clear(ln_k);
        mpfr_clear(ln_ln_k);
        mpfr_clear(z5d_estimate);
        mpfr_clear(correction_term);
        mpfr_clear(kappa_star_mpfr);
        mpfr_clear(temp);
        mpz_clear(estimated_prime);
    }

    // Fallback: random 2048-bit prime (simplified)
    unsigned char prime_seed[256];
    derive_seed(cfg->seed, label ? label : "prime", prime_seed, sizeof(prime_seed));
    seed_to_2048bit(prime_seed, prime_out);

    for (unsigned long attempt = 0; attempt < 10000UL; ++attempt) {
        if (candidate_is_probable_prime(prime_out, cfg, 0)) {
            return 1;
        }
        mpz_add_ui(prime_out, prime_out, 2);
    }

    return 0;
}

// Rest of the original functions remain the same

void init_mpfr() {
    mpfr_set_default_prec(MPFR_PRECISION);
    mpfr_init(mpfr_phi);
    mpfr_init(temp1);
    mpfr_init(temp2);
    mpfr_init(temp3);
    
    mpfr_set_d(mpfr_phi, PHI, MPFR_RNDN);

    if (golden_spiral_init(GOLDEN_SPIRAL_PRECISION) != 0) {
        fprintf(stderr, "Failed to initialize golden spiral\n");
        exit(1);
    }
}

void cleanup_mpfr() {
    mpfr_clear(mpfr_phi);
    mpfr_clear(temp1);
    mpfr_clear(temp2);
    mpfr_clear(temp3);

    golden_spiral_cleanup();
}

double compute_geometric_coordinate(mpfr_t n_mpfr, double k) {
    mpfr_div(temp2, n_mpfr, mpfr_phi, MPFR_RNDN);
    mpfr_frac(temp2, temp2, MPFR_RNDN);
    mpfr_set_d(temp3, k, MPFR_RNDN);
    mpfr_pow(temp2, temp2, temp3, MPFR_RNDN);
    mpfr_mul(temp1, temp2, mpfr_phi, MPFR_RNDN);
    mpfr_frac(temp1, temp1, MPFR_RNDN);
    return mpfr_get_d(temp1, MPFR_RNDN);
}

double circ_dist(double a, double b) {
    double d = fmod(a - b + 0.5, 1.0) - 0.5;
    return fabs(d);
}

int is_prime(mpz_t n) {
    return mpz_probab_prime_p(n, 15) > 0;
}

int generate_candidates(mpz_t candidates[], mpfr_t N_mpfr, double k, double eps) {
    double theta_N = compute_geometric_coordinate(N_mpfr, k);
    int count = 0;
    mpz_t p;
    mpz_init_set_ui(p, 2);
    mpz_t sqrt_N;
    mpz_init(sqrt_N);
    mpz_t N_z;
    mpz_init(N_z);
    mpfr_get_z(N_z, N_mpfr, MPFR_RNDN);
    mpz_sqrt(sqrt_N, N_z);
    mpz_t max_p;
    mpz_init_set_ui(max_p, 100000);
    if (mpz_cmp(sqrt_N, max_p) > 0) {
        mpz_set(sqrt_N, max_p);
    }
    while (mpz_cmp(p, sqrt_N) <= 0 && count < MAX_CANDIDATES) {
        if (is_prime(p)) {
            mpfr_t p_mpfr;
            mpfr_init(p_mpfr);
            mpfr_set_z(p_mpfr, p, MPFR_RNDN);
            double theta_p = compute_geometric_coordinate(p_mpfr, k);
            mpfr_clear(p_mpfr);
            if (circ_dist(theta_p, theta_N) <= eps) {
                mpz_set(candidates[count], p);
                count++;
            }
        }
        mpz_nextprime(p, p);
    }
    mpz_clear(p);
    mpz_clear(sqrt_N);
    mpz_clear(N_z);
    mpz_clear(max_p);

    // Add spiral candidates
    spiral_params_t params;
    if (spiral_params_init(&params, 0.0, 1.0, 1.0, 100) != 0) {
        return count;
    }
    mpfr_t sqrt_N_mpfr;
    mpfr_init(sqrt_N_mpfr);
    mpfr_sqrt(sqrt_N_mpfr, N_mpfr, MPFR_RNDN);
    mpfr_set(params.center, sqrt_N_mpfr, MPFR_RNDN);
    mpfr_set_d(params.r_scale, 100.0, MPFR_RNDN);
    mpfr_set_d(params.s_scale, 50.0, MPFR_RNDN);
    params.max_iterations = 100;
    spiral_candidate_t spiral_cands[100];
    for(int i = 0; i < 100; i++) spiral_candidate_init(&spiral_cands[i]);
    int found;
    if (golden_spiral_search(&params, spiral_cands, 100, &found) == 0) {
        for(int i = 0; i < found && count < MAX_CANDIDATES; i++) {
            mpfr_t cand_mpfr;
            mpfr_init(cand_mpfr);
            mpfr_set(cand_mpfr, spiral_cands[i].value, MPFR_RNDN);
            if (mpfr_integer_p(cand_mpfr)) {
                mpz_t cand_z;
                mpz_init(cand_z);
                mpfr_get_z(cand_z, cand_mpfr, MPFR_RNDN);
                if (is_prime(cand_z)) {
                    mpfr_t p_mpfr;
                    mpfr_init(p_mpfr);
                    mpfr_set_z(p_mpfr, cand_z, MPFR_RNDN);
                    double theta_p = compute_geometric_coordinate(p_mpfr, k);
                    mpfr_clear(p_mpfr);
                    if (circ_dist(theta_p, theta_N) <= eps) {
                        int duplicate = 0;
                        for(int j = 0; j < count; j++) {
                            if (mpz_cmp(candidates[j], cand_z) == 0) {
                                duplicate = 1;
                                break;
                            }
                        }
                        if (!duplicate) {
                            mpz_set(candidates[count], cand_z);
                            count++;
                        }
                    }
                }
                mpz_clear(cand_z);
            }
            mpfr_clear(cand_mpfr);
        }
    }
    for(int i = 0; i < 100; i++) spiral_candidate_cleanup(&spiral_cands[i]);
    spiral_params_cleanup(&params);
    mpfr_clear(sqrt_N_mpfr);

    return count;
}

int geometric_factorize(mpz_t N, mpfr_t N_mpfr, double k, double eps, mpz_t p_out, mpz_t q_out) {
    mpz_t candidates[MAX_CANDIDATES];
    for (int i = 0; i < MAX_CANDIDATES; i++) mpz_init(candidates[i]);
    int n_cand = generate_candidates(candidates, N_mpfr, k, eps);
    
    for (int i = 0; i < n_cand; i++) {
        mpz_t p;
        mpz_init_set(p, candidates[i]);
        if (mpz_divisible_p(N, p)) {
            mpz_t q;
            mpz_init(q);
            mpz_divexact(q, N, p);
            if (is_prime(q)) {
                mpz_set(p_out, p);
                mpz_set(q_out, q);
                for (int j = 0; j < MAX_CANDIDATES; j++) mpz_clear(candidates[j]);
                mpz_clear(p);
                mpz_clear(q);
                return 1;
            }
            mpz_clear(q);
        }
        mpz_clear(p);
    }
    for (int j = 0; j < MAX_CANDIDATES; j++) mpz_clear(candidates[j]);
    return 0;
}

int multi_pass_factorize(mpz_t N, mpfr_t N_mpfr, mpz_t p_out, mpz_t q_out) {
    double k_sequence[] = {0.200, 0.450, 0.800, 0.300, 0.600, 0.100, 0.700, 0.250, 0.550};
    double eps_sequence[] = {0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10};
    int n_k = sizeof(k_sequence) / sizeof(double);
    int n_eps = sizeof(eps_sequence) / sizeof(double);
    
    for (int i = 0; i < n_k; i++) {
        for (int j = 0; j < n_eps; j++) {
            if (geometric_factorize(N, N_mpfr, k_sequence[i], eps_sequence[j], p_out, q_out)) {
                return 1;
            }
        }
    }
    return 0;
}

void generate_semiprimes(mpz_t semiprimes_N[], mpz_t semiprimes_p[], mpz_t semiprimes_q[], int *count, int samples, int bit_size, unsigned int seed) {
    *count = 0;
    int prime_bits = bit_size / 2;
    config_t cfg;
    if (init_config(&cfg) != ZSEED_OK) {
        fprintf(stderr, "Failed to initialize seed\n");
        return;
    }
    
    // Use seed for randomness in x selection
    gmp_randstate_t state;
    gmp_randinit_default(state);
    gmp_randseed_ui(state, seed);
    
    while (*count < samples) {
        mpz_t p, q, N;
        mpz_init(p);
        mpz_init(q);
        mpz_init(N);
        
        // Generate random x in the bit range for p
        mpz_t x_p;
        mpz_init(x_p);
        mpz_urandomb(x_p, state, prime_bits);
        mpz_setbit(x_p, prime_bits - 1);  // Ensure high bit set
        
        // Compute k for p
        mpz_t k_p;
        mpz_init(k_p);
        z5d_prime_count(x_p, k_p, &cfg);
        
        // Get prime p
        if (!z5d_nth_prime("p", k_p, p, &cfg, NULL, 0)) {
            fprintf(stderr, "Failed to generate prime p\n");
            mpz_clear(x_p);
            mpz_clear(k_p);
            continue;
        }
        
        // Similarly for q
        mpz_t x_q;
        mpz_init(x_q);
        mpz_urandomb(x_q, state, prime_bits);
        mpz_setbit(x_q, prime_bits - 1);
        
        mpz_t k_q;
        mpz_init(k_q);
        z5d_prime_count(x_q, k_q, &cfg);
        
        // Ensure q != p
        int attempts = 0;
        while (attempts < 10) {
            if (!z5d_nth_prime("q", k_q, q, &cfg, &p, 1)) {
                fprintf(stderr, "Failed to generate prime q\n");
                break;
            }
            if (mpz_cmp(p, q) != 0) break;
            mpz_add_ui(k_q, k_q, 1);
            attempts++;
        }
        if (attempts >= 10 || mpz_cmp(p, q) == 0) {
            mpz_clear(x_p);
            mpz_clear(k_p);
            mpz_clear(x_q);
            mpz_clear(k_q);
            continue;
        }
        
        if (mpz_cmp(p, q) > 0) mpz_swap(p, q);
        mpz_mul(N, p, q);
        
        mpz_set(semiprimes_N[*count], N);
        mpz_set(semiprimes_p[*count], p);
        mpz_set(semiprimes_q[*count], q);
        (*count)++;
        
        mpz_clear(p);
        mpz_clear(q);
        mpz_clear(N);
        mpz_clear(x_p);
        mpz_clear(k_p);
        mpz_clear(x_q);
        mpz_clear(k_q);
    }
    gmp_randclear(state);
}

int main(int argc, char *argv[]) {
    init_mpfr();
    
    int samples = 10;
    int bit_size = 64;
    if (argc > 1) samples = atoi(argv[1]);
    if (argc > 2) bit_size = atoi(argv[2]);
    
    const int max_s = 1000;
    mpz_t semiprimes_N[max_s];
    mpz_t semiprimes_p[max_s];
    mpz_t semiprimes_q[max_s];
    for (int i = 0; i < max_s; i++) {
        mpz_init(semiprimes_N[i]);
        mpz_init(semiprimes_p[i]);
        mpz_init(semiprimes_q[i]);
    }
    int n_semiprimes;
    generate_semiprimes(semiprimes_N, semiprimes_p, semiprimes_q, &n_semiprimes, samples, bit_size, 42);
    
    int successes = 0;
    FILE *log_file = fopen("logs/factorization_log.txt", "w");
    FILE *success_file = fopen("logs/success_log.txt", "w");
    FILE *fail_file = fopen("logs/fail_log.txt", "w");
    
    if (!log_file || !success_file || !fail_file) {
        printf("Error opening log files\n");
        return 1;
    }
    
    fprintf(log_file, "Geometric Factorization Test Results\n");
    fprintf(log_file, "Samples: %d\n", samples);
    fprintf(log_file, "Bit size: %d\n", bit_size);
    fprintf(log_file, "Target: Success rate > 0%%\n\n");
    
    for (int i = 0; i < n_semiprimes; i++) {
        mpz_t N, expected_p, expected_q, found_p, found_q;
        mpz_init_set(N, semiprimes_N[i]);
        mpz_init_set(expected_p, semiprimes_p[i]);
        mpz_init_set(expected_q, semiprimes_q[i]);
        mpz_init(found_p);
        mpz_init(found_q);
        
        mpfr_t N_mpfr;
        mpfr_init(N_mpfr);
        mpfr_set_z(N_mpfr, N, MPFR_RNDN);
        
        int success = multi_pass_factorize(N, N_mpfr, found_p, found_q);
        gmp_fprintf(log_file, "N=%Zd, Expected: %Zd x %Zd, ", N, expected_p, expected_q);
        if (success) {
            successes++;
            gmp_fprintf(log_file, "SUCCESS: Found %Zd x %Zd\n", found_p, found_q);
            gmp_fprintf(success_file, "%Zd = %Zd x %Zd\n", N, found_p, found_q);
        } else {
            gmp_fprintf(log_file, "FAILED\n");
            gmp_fprintf(fail_file, "%Zd (expected %Zd x %Zd)\n", N, expected_p, expected_q);
        }
        
        mpfr_clear(N_mpfr);
        mpz_clear(N);
        mpz_clear(expected_p);
        mpz_clear(expected_q);
        mpz_clear(found_p);
        mpz_clear(found_q);
    }
    
    double rate = (double)successes / n_semiprimes * 100;
    fprintf(log_file, "\nSuccess Rate: %.2f%% (%d/%d)\n", rate, successes, n_semiprimes);
    printf("Success Rate: %.2f%% (%d/%d)\n", rate, successes, n_semiprimes);
    
    if (rate > 0.0) {
        fprintf(log_file, "GOAL ACHIEVED: Success rate > 0%%\n");
        printf("GOAL ACHIEVED: Success rate > 0%%\n");
    } else {
        fprintf(log_file, "GOAL NOT ACHIEVED: Need to improve further\n");
        printf("GOAL NOT ACHIEVED: Need to improve further\n");
    }
    
    fclose(log_file);
    fclose(success_file);
    fclose(fail_file);
    
    for (int i = 0; i < max_s; i++) {
        mpz_clear(semiprimes_N[i]);
        mpz_clear(semiprimes_p[i]);
        mpz_clear(semiprimes_q[i]);
    }
    
    cleanup_mpfr();
    return 0;
}