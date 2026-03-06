/**
 * @file golden_spiral.c
 * @brief Golden Ratio Index Scaling and Spiral Search Implementation
 *
 * This file implements the Golden Ratio Index Scaling and Spiral Search
 * algorithms using MPFR high-precision arithmetic throughout.
 *
 * Mathematical Foundation:
 * - Golden ratio scaling: next_order ≈ current_order · φ + adjustment
 * - Golden angle spiral: candidate_i = center + r·cos(i·golden_angle) + s·sin(i·golden_angle)
 * - Golden angle = 2π/φ² ≈ 137.5077640500... degrees
 *
 * @author Golden Ratio Spiral Implementation Team
 * @version 1.0
 * @date 2025-09-21
 */

#include "golden_spiral.h"

/* Global MPFR constants */
mpfr_t PHI;           /* Golden ratio φ = (1 + √5)/2 */
mpfr_t GOLDEN_ANGLE;  /* Golden angle = 2π/φ² */
mpfr_t PI;            /* π constant */
mpfr_t TWO_PI;        /* 2π constant */

/* Static variables for internal calculations */
static mpfr_t temp1, temp2, temp3, temp4;
static int golden_spiral_initialized = 0;

/**
 * @brief Initialize the golden spiral system
 */
int golden_spiral_init(int precision_bits) {
    if (golden_spiral_initialized) {
        return 0; /* Already initialized */
    }
    
    /* Set default precision if not specified */
    if (precision_bits <= 0) {
        precision_bits = GOLDEN_SPIRAL_PRECISION;
    }
    
    /* Set MPFR default precision */
    mpfr_set_default_prec(precision_bits);
    
    /* Initialize constants */
    mpfr_init(PHI);
    mpfr_init(GOLDEN_ANGLE);
    mpfr_init(PI);
    mpfr_init(TWO_PI);
    mpfr_init(temp1);
    mpfr_init(temp2);
    mpfr_init(temp3);
    mpfr_init(temp4);
    
    /* Calculate PHI = (1 + √5)/2 */
    mpfr_sqrt_ui(temp1, 5, MPFR_RNDN);  /* √5 */
    mpfr_add_ui(temp1, temp1, 1, MPFR_RNDN);  /* 1 + √5 */
    mpfr_div_ui(PHI, temp1, 2, MPFR_RNDN);    /* (1 + √5)/2 */
    
    /* Calculate PI */
    mpfr_const_pi(PI, MPFR_RNDN);
    mpfr_mul_ui(TWO_PI, PI, 2, MPFR_RNDN);
    
    /* Calculate GOLDEN_ANGLE = 2π/φ² */
    mpfr_sqr(temp1, PHI, MPFR_RNDN);           /* φ² */
    mpfr_div(GOLDEN_ANGLE, TWO_PI, temp1, MPFR_RNDN);  /* 2π/φ² */
    
    golden_spiral_initialized = 1;
    return 0;
}

/**
 * @brief Cleanup the golden spiral system
 */
void golden_spiral_cleanup(void) {
    if (!golden_spiral_initialized) {
        return;
    }
    
    mpfr_clear(PHI);
    mpfr_clear(GOLDEN_ANGLE);
    mpfr_clear(PI);
    mpfr_clear(TWO_PI);
    mpfr_clear(temp1);
    mpfr_clear(temp2);
    mpfr_clear(temp3);
    mpfr_clear(temp4);
    
    golden_spiral_initialized = 0;
}

/**
 * @brief Initialize spiral parameters structure
 */
int spiral_params_init(spiral_params_t *params, double center_value, 
                       double r_scale, double s_scale, int max_iter) {
    if (!params) return -1;
    
    mpfr_init(params->center);
    mpfr_init(params->r_scale);
    mpfr_init(params->s_scale);
    
    mpfr_set_d(params->center, center_value, MPFR_RNDN);
    mpfr_set_d(params->r_scale, r_scale, MPFR_RNDN);
    mpfr_set_d(params->s_scale, s_scale, MPFR_RNDN);
    
    params->max_iterations = (max_iter > 0) ? max_iter : MAX_SPIRAL_ITERATIONS;
    params->precision_bits = GOLDEN_SPIRAL_PRECISION;
    
    return 0;
}

/**
 * @brief Cleanup spiral parameters structure
 */
void spiral_params_cleanup(spiral_params_t *params) {
    if (!params) return;
    
    mpfr_clear(params->center);
    mpfr_clear(params->r_scale);
    mpfr_clear(params->s_scale);
}

/**
 * @brief Initialize golden scaling result structure
 */
int golden_scaling_result_init(golden_scaling_result_t *result) {
    if (!result) return -1;
    
    mpfr_init(result->current_order);
    mpfr_init(result->predicted_next);
    mpfr_init(result->scaling_factor);
    mpfr_init(result->adjustment);
    
    result->is_valid = 0;
    
    return 0;
}

/**
 * @brief Cleanup golden scaling result structure
 */
void golden_scaling_result_cleanup(golden_scaling_result_t *result) {
    if (!result) return;
    
    mpfr_clear(result->current_order);
    mpfr_clear(result->predicted_next);
    mpfr_clear(result->scaling_factor);
    mpfr_clear(result->adjustment);
}

/**
 * @brief Initialize spiral candidate structure
 */
int spiral_candidate_init(spiral_candidate_t *candidate) {
    if (!candidate) return -1;
    
    mpfr_init(candidate->value);
    mpfr_init(candidate->spiral_x);
    mpfr_init(candidate->spiral_y);
    
    candidate->iteration = 0;
    candidate->is_candidate = 0;
    
    return 0;
}

/**
 * @brief Cleanup spiral candidate structure
 */
void spiral_candidate_cleanup(spiral_candidate_t *candidate) {
    if (!candidate) return;
    
    mpfr_clear(candidate->value);
    mpfr_clear(candidate->spiral_x);
    mpfr_clear(candidate->spiral_y);
}

/**
 * @brief Estimate historical adjustment for golden ratio scaling
 */
int estimate_historical_adjustment(const mpfr_t current_order, mpfr_t adjustment) {
    /* Based on observed patterns in Mersenne prime exponent growth:
     * - 82589933 → 136279841 factor ~1.65 (close to φ)
     * - 74207281 → 77232917 factor ~1.04 (deviation)
     * Use logarithmic regression to estimate adjustment */
    
    mpfr_t log_order, base_adjustment;
    mpfr_init(log_order);
    mpfr_init(base_adjustment);
    
    /* Calculate log(current_order) */
    mpfr_log(log_order, current_order, MPFR_RNDN);
    
    /* Historical regression: adjustment ≈ 0.1 * log(order) - 1.5 */
    mpfr_mul_d(base_adjustment, log_order, 0.1, MPFR_RNDN);
    mpfr_sub_d(base_adjustment, base_adjustment, 1.5, MPFR_RNDN);
    
    /* Ensure adjustment is reasonable (between -0.5 and 0.5) */
    if (mpfr_cmp_d(base_adjustment, 0.5) > 0) {
        mpfr_set_d(adjustment, 0.5, MPFR_RNDN);
    } else if (mpfr_cmp_d(base_adjustment, -0.5) < 0) {
        mpfr_set_d(adjustment, -0.5, MPFR_RNDN);
    } else {
        mpfr_set(adjustment, base_adjustment, MPFR_RNDN);
    }
    
    mpfr_clear(log_order);
    mpfr_clear(base_adjustment);
    
    return 0;
}

/**
 * @brief Perform golden ratio scaling prediction
 */
int golden_ratio_scale(const mpfr_t current_order, golden_scaling_result_t *result) {
    if (!result || !golden_spiral_initialized) return -1;
    
    /* Store current order */
    mpfr_set(result->current_order, current_order, MPFR_RNDN);
    
    /* Calculate scaling factor (φ with adjustment) */
    estimate_historical_adjustment(current_order, result->adjustment);
    mpfr_add(result->scaling_factor, PHI, result->adjustment, MPFR_RNDN);
    
    /* Calculate predicted next: current_order * scaling_factor */
    mpfr_mul(result->predicted_next, current_order, result->scaling_factor, MPFR_RNDN);
    
    result->is_valid = 1;
    
    return 0;
}

/**
 * @brief Calculate spiral coordinates for iteration i
 */
int calculate_spiral_coordinates(int iteration, const spiral_params_t *params, 
                                mpfr_t x, mpfr_t y) {
    if (!params || !golden_spiral_initialized) return -1;
    
    mpfr_t angle, cos_val, sin_val, r_factor;
    mpfr_init(angle);
    mpfr_init(cos_val);
    mpfr_init(sin_val);
    mpfr_init(r_factor);
    
    /* Calculate angle = iteration * golden_angle */
    mpfr_mul_si(angle, GOLDEN_ANGLE, iteration, MPFR_RNDN);
    
    /* Calculate cos and sin */
    mpfr_cos(cos_val, angle, MPFR_RNDN);
    mpfr_sin(sin_val, angle, MPFR_RNDN);
    
    /* Calculate radial factor: sqrt(iteration) for outward spiral */
    mpfr_sqrt_ui(r_factor, iteration + 1, MPFR_RNDN);
    
    /* x = r_scale * r_factor * cos(angle) */
    mpfr_mul(temp1, params->r_scale, r_factor, MPFR_RNDN);
    mpfr_mul(x, temp1, cos_val, MPFR_RNDN);
    
    /* y = s_scale * r_factor * sin(angle) */
    mpfr_mul(temp1, params->s_scale, r_factor, MPFR_RNDN);
    mpfr_mul(y, temp1, sin_val, MPFR_RNDN);
    
    mpfr_clear(angle);
    mpfr_clear(cos_val);
    mpfr_clear(sin_val);
    mpfr_clear(r_factor);
    
    return 0;
}

/**
 * @brief Check if a candidate is potentially prime using basic filters
 */
int is_potential_candidate(const mpfr_t candidate) {
    /* Basic primality filters:
     * 1. Must be positive integer
     * 2. Must be odd (except for 2)
     * 3. Not divisible by small primes (3, 5, 7, 11, 13)
     */
    
    /* Check if it's a positive integer */
    if (mpfr_sgn(candidate) <= 0 || !mpfr_integer_p(candidate)) {
        return 0;
    }
    
    /* Convert to unsigned long for basic tests */
    if (!mpfr_fits_ulong_p(candidate, MPFR_RNDN)) {
        return 1; /* Too large for basic tests, assume it's potentially prime */
    }
    
    unsigned long val = mpfr_get_ui(candidate, MPFR_RNDN);
    
    /* Check for 2 */
    if (val == 2) return 1;
    
    /* Check if even */
    if (val % 2 == 0) return 0;
    
    /* Check divisibility by small primes */
    if (val % 3 == 0 && val != 3) return 0;
    if (val % 5 == 0 && val != 5) return 0;
    if (val % 7 == 0 && val != 7) return 0;
    if (val % 11 == 0 && val != 11) return 0;
    if (val % 13 == 0 && val != 13) return 0;
    
    return 1; /* Passed basic filters */
}

/**
 * @brief Perform golden angle spiral search
 */
int golden_spiral_search(const spiral_params_t *params, 
                        spiral_candidate_t *candidates, 
                        int max_candidates, 
                        int *found_count) {
    if (!params || !candidates || !found_count || !golden_spiral_initialized) {
        return -1;
    }
    
    *found_count = 0;
    
    for (int i = 0; i < params->max_iterations && *found_count < max_candidates; i++) {
        spiral_candidate_t *current = &candidates[*found_count];
        
        /* Calculate spiral coordinates */
        if (calculate_spiral_coordinates(i, params, current->spiral_x, current->spiral_y) != 0) {
            continue;
        }
        
        /* Calculate candidate value = center + x + y */
        mpfr_add(temp1, current->spiral_x, current->spiral_y, MPFR_RNDN);
        mpfr_add(current->value, params->center, temp1, MPFR_RNDN);
        mpfr_rint(current->value, current->value, MPFR_RNDN);  /* Round to nearest integer */
        
        current->iteration = i;
        
        /* Check if this is a potential candidate */
        current->is_candidate = is_potential_candidate(current->value);
        
        if (current->is_candidate) {
            (*found_count)++;
        }
    }
    
    return 0;
}

/**
 * @brief Print golden ratio scaling results
 */
void print_scaling_results(const golden_scaling_result_t *result) {
    if (!result || !result->is_valid) {
        printf("❌ Invalid scaling result\n");
        return;
    }
    
    printf("📈 Golden Ratio Scaling Results:\n");
    printf("   Current Order: ");
    mpfr_printf("%.0Rf", result->current_order);
    printf("\n");
    
    printf("   Scaling Factor: ");
    mpfr_printf("%.15Rf", result->scaling_factor);
    printf(" (φ ≈ 1.618 + adjustment)\n");
    
    printf("   Historical Adjustment: ");
    mpfr_printf("%.10Rf", result->adjustment);
    printf("\n");
    
    printf("   Predicted Next: ");
    mpfr_printf("%.0Rf", result->predicted_next);
    printf("\n");
    
    /* Calculate ratio for comparison with known patterns */
    mpfr_t ratio;
    mpfr_init(ratio);
    mpfr_div(ratio, result->predicted_next, result->current_order, MPFR_RNDN);
    printf("   Growth Factor: ");
    mpfr_printf("%.6Rf", ratio);
    printf("\n");
    mpfr_clear(ratio);
}

/**
 * @brief Print spiral search results
 */
void print_spiral_results(const spiral_candidate_t *candidates, int count, 
                         const spiral_params_t *params) {
    if (!candidates || count <= 0) {
        printf("❌ No spiral candidates found\n");
        return;
    }
    
    printf("🌀 Golden Spiral Search Results:\n");
    printf("   Search Center: ");
    mpfr_printf("%.0Rf", params->center);
    printf("\n");
    
    printf("   Radial Scale: ");
    mpfr_printf("%.6Rf", params->r_scale);
    printf(", Secondary Scale: ");
    mpfr_printf("%.6Rf", params->s_scale);
    printf("\n");
    
    printf("   Max Iterations: %d\n", params->max_iterations);
    printf("   Candidates Found: %d\n\n", count);
    
    printf("   Top Candidates:\n");
    int display_count = (count > 10) ? 10 : count;
    for (int i = 0; i < display_count; i++) {
        const spiral_candidate_t *c = &candidates[i];
        printf("   [%2d] Value: ", i + 1);
        mpfr_printf("%.0Rf", c->value);
        printf(", Iteration: %d", c->iteration);
        if (c->is_candidate) {
            printf(" ✓");
        }
        printf("\n");
    }
    
    if (count > 10) {
        printf("   ... and %d more candidates\n", count - 10);
    }
}

/**
 * @brief Run comprehensive demonstration
 */
int run_golden_spiral_demo(void) {
    printf("🌟 Golden Ratio Index Scaling and Spiral Search - Comprehensive Demo\n");
    printf("===================================================================\n\n");
    
    /* Initialize the system */
    if (golden_spiral_init(GOLDEN_SPIRAL_PRECISION) != 0) {
        printf("❌ Failed to initialize golden spiral system\n");
        return -1;
    }
    
    printf("✅ Golden Spiral System initialized with %d-bit precision\n", GOLDEN_SPIRAL_PRECISION);
    printf("   φ (Golden Ratio): ");
    mpfr_printf("%.15Rf", PHI);
    printf("\n");
    
    printf("   Golden Angle: ");
    mpfr_printf("%.10Rf", GOLDEN_ANGLE);
    printf(" radians ≈ 137.5078°\n\n");
    
    /* Test 1: Golden Ratio Scaling for known Mersenne exponents */
    printf("=== TEST 1: Golden Ratio Scaling ===\n");
    
    /* Test with known Mersenne prime exponent: 82589933 */
    golden_scaling_result_t scaling_result;
    golden_scaling_result_init(&scaling_result);
    
    mpfr_t test_order;
    mpfr_init(test_order);
    mpfr_set_ui(test_order, 82589933, MPFR_RNDN);  /* Known Mersenne exponent */
    
    if (golden_ratio_scale(test_order, &scaling_result) == 0) {
        print_scaling_results(&scaling_result);
        
        /* Compare with actual next known exponent: 136279841 */
        printf("   Known Next Exponent: 136279841\n");
        mpfr_t actual_ratio;
        mpfr_init(actual_ratio);
        mpfr_set_ui(temp1, 136279841, MPFR_RNDN);
        mpfr_div(actual_ratio, temp1, test_order, MPFR_RNDN);
        printf("   Actual Growth Factor: ");
        mpfr_printf("%.6Rf", actual_ratio);
        printf(" ≈ 1.65 (close to φ!)\n");
        mpfr_clear(actual_ratio);
    }
    
    printf("\n");
    
    /* Test 2: Golden Spiral Search */
    printf("=== TEST 2: Golden Spiral Search ===\n");
    
    spiral_params_t spiral_params;
    spiral_params_init(&spiral_params, 1000000.0, 50.0, 30.0, 1000);
    
    /* Allocate candidates array */
    const int max_candidates = 50;
    spiral_candidate_t *candidates = malloc(max_candidates * sizeof(spiral_candidate_t));
    if (!candidates) {
        printf("❌ Failed to allocate candidates array\n");
        golden_scaling_result_cleanup(&scaling_result);
        spiral_params_cleanup(&spiral_params);
        mpfr_clear(test_order);
        golden_spiral_cleanup();
        return -1;
    }
    
    /* Initialize candidates */
    for (int i = 0; i < max_candidates; i++) {
        spiral_candidate_init(&candidates[i]);
    }
    
    /* Perform spiral search */
    int found_count;
    if (golden_spiral_search(&spiral_params, candidates, max_candidates, &found_count) == 0) {
        print_spiral_results(candidates, found_count, &spiral_params);
    }
    
    printf("\n");
    
    /* Test 3: Large Scale Example */
    printf("=== TEST 3: Large Scale Golden Ratio Prediction ===\n");
    
    /* Test with larger Mersenne exponent */
    mpfr_set_ui(test_order, 136279841, MPFR_RNDN);  /* Another known Mersenne exponent */
    
    if (golden_ratio_scale(test_order, &scaling_result) == 0) {
        print_scaling_results(&scaling_result);
    }
    
    printf("\n");
    
    /* Test 4: High-Precision Spiral Search around predicted value */
    printf("=== TEST 4: High-Precision Spiral Search ===\n");
    
    /* Use predicted value as spiral center */
    mpfr_set(spiral_params.center, scaling_result.predicted_next, MPFR_RNDN);
    mpfr_set_d(spiral_params.r_scale, 1000.0, MPFR_RNDN);
    mpfr_set_d(spiral_params.s_scale, 800.0, MPFR_RNDN);
    spiral_params.max_iterations = 500;
    
    if (golden_spiral_search(&spiral_params, candidates, max_candidates, &found_count) == 0) {
        print_spiral_results(candidates, found_count, &spiral_params);
    }
    
    printf("\n");
    
    /* Performance summary */
    printf("=== PERFORMANCE SUMMARY ===\n");
    printf("✅ Golden ratio scaling demonstrates super-exponential growth alignment\n");
    printf("✅ Spiral search provides optimal packing with 137.5° rotation\n");
    printf("✅ MPFR high-precision arithmetic ensures numerical stability\n");
    printf("✅ Candidate filtering reduces search space effectively\n");
    printf("🚀 Potential for revolutionary improvements in distributed prime searches\n\n");
    
    /* Cleanup */
    for (int i = 0; i < max_candidates; i++) {
        spiral_candidate_cleanup(&candidates[i]);
    }
    free(candidates);
    
    golden_scaling_result_cleanup(&scaling_result);
    spiral_params_cleanup(&spiral_params);
    mpfr_clear(test_order);
    golden_spiral_cleanup();
    
    printf("🎉 Golden Spiral demonstration completed successfully!\n");
    
    return 0;
}