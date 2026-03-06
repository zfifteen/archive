#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <mpfr.h>

#include "modular_progressions.h"
#include "crypto_analysis.h"
#include "dual_ec_analysis.h"
#include "sha256_bounds.h"

/**
 * @file modular_geometric_progressions.c
 * @brief Main executable for Modular Geometric Progressions in Cryptographic Analysis
 * 
 * Command-line tool for analyzing cryptographic systems using modular geometric progressions
 * and Z Framework principles including:
 * - Scalar analogy for Dual_EC_DRBG
 * - Modular geometric bounds for SHA-256 constants  
 * - Z Framework applications to cryptographic primitives
 */

// Command line options
static struct option long_options[] = {
    {"progression",     required_argument, 0, 'p'},
    {"dual-ec",         no_argument,       0, 'd'},
    {"sha256-bounds",   no_argument,       0, 's'},
    {"crypto-strength", no_argument,       0, 'c'},
    {"generate-terms",  required_argument, 0, 'g'},
    {"analyze-period",  no_argument,       0, 'P'},
    {"geodesic",        required_argument, 0, 'G'},
    {"precision",       required_argument, 0, 'r'},
    {"verbose",         no_argument,       0, 'v'},
    {"output",          required_argument, 0, 'o'},
    {"validate",        no_argument,       0, 'V'},
    {"help",            no_argument,       0, 'h'},
    {0, 0, 0, 0}
};

typedef struct {
    unsigned long base;
    unsigned long ratio;
    unsigned long modulus;
    unsigned long terms;
    bool analyze_dual_ec;
    bool analyze_sha256;
    bool analyze_crypto_strength;
    int generate_terms;
    bool analyze_period;
    double kappa_geo;
    unsigned int precision_bits;
    bool verbose;
    bool validate;
    char *output_file;
} program_options_t;

void print_help(const char *program_name) {
    printf("Modular Geometric Progressions in Cryptographic Analysis\n");
    printf("=======================================================\n\n");
    
    printf("Usage: %s [OPTIONS]\n\n", program_name);
    
    printf("Options:\n");
    printf("  -p, --progression BASE,RATIO,MOD  Set progression parameters (base,ratio,modulus)\n");
    printf("  -d, --dual-ec                     Analyze Dual_EC_DRBG scalar analogy\n");
    printf("  -s, --sha256-bounds               Analyze SHA-256 constant bounds\n");
    printf("  -c, --crypto-strength             Analyze cryptographic strength\n");
    printf("  -g, --generate-terms N            Generate N terms of the progression\n");
    printf("  -P, --analyze-period              Analyze progression period\n");
    printf("  -G, --geodesic KAPPA              Use geodesic enhancement (default: 0.3)\n");
    printf("  -r, --precision BITS              MPFR precision in bits (default: 256)\n");
    printf("  -v, --verbose                     Enable verbose output\n");
    printf("  -o, --output FILE                 Output results to file\n");
    printf("  -V, --validate                    Validate Z Framework principles\n");
    printf("  -h, --help                        Show this help message\n\n");
    
    printf("Examples:\n");
    printf("  %s -p 3,7,1024 -g 10 -v\n", program_name);
    printf("  %s -p 5,11,2048 -d -s -c\n", program_name);
    printf("  %s -p 2,3,65537 -P -G 0.5 -V\n", program_name);
    printf("  %s -p 7,13,4096 --sha256-bounds --output results.txt\n\n", program_name);
    
    printf("Z Framework Integration:\n");
    printf("  • Uses geodesic mapping with κ_geo parameter (default: 0.3)\n");
    printf("  • Applies κ_star parameter for cryptographic calibration (0.04449)\n");
    printf("  • High-precision MPFR arithmetic (256-bit default)\n");
    printf("  • Cross-domain analysis connecting discrete and cryptographic domains\n\n");
    
    printf("Theory:\n");
    printf("  Modular geometric progressions: a, ar (mod m), ar² (mod m), ...\n");
    printf("  Applied to cryptographic analysis via Z Framework principles\n");
    printf("  Dual_EC_DRBG scalar analogy for elliptic curve operations\n");
    printf("  SHA-256 constant bounds using geometric progression analysis\n\n");
}

bool parse_progression_params(const char *param_str, program_options_t *opts) {
    size_t len = strlen(param_str);
    char *str_copy = malloc(len + 1);
    strcpy(str_copy, param_str);
    
    char *token;
    int param_count = 0;
    
    token = strtok(str_copy, ",");
    while (token != NULL && param_count < 3) {
        unsigned long value = strtoul(token, NULL, 10);
        if (value == 0 && strcmp(token, "0") != 0) {
            printf("❌ Error: Invalid parameter '%s'\n", token);
            free(str_copy);
            return false;
        }
        
        switch (param_count) {
            case 0: opts->base = value; break;
            case 1: opts->ratio = value; break;
            case 2: opts->modulus = value; break;
        }
        
        param_count++;
        token = strtok(NULL, ",");
    }
    
    free(str_copy);
    
    if (param_count != 3) {
        printf("❌ Error: Expected 3 parameters (base,ratio,modulus), got %d\n", param_count);
        return false;
    }
    
    return true;
}

void print_progression_info(const program_options_t *opts) {
    printf("📊 Modular Geometric Progression Parameters:\n");
    printf("   Base (a):     %lu\n", opts->base);
    printf("   Ratio (r):    %lu\n", opts->ratio);
    printf("   Modulus (m):  %lu\n", opts->modulus);
    printf("   κ_geo:        %.6f (Z Framework geodesic exponent)\n", opts->kappa_geo);
    printf("   Precision:    %u bits MPFR\n", opts->precision_bits);
    printf("\n");
}

void analyze_dual_ec(const program_options_t *opts) {
    printf("🔐 Dual_EC_DRBG Scalar Analogy Analysis\n");
    printf("=====================================\n");
    
    dual_ec_state_t state;
    dual_ec_init(&state);
    
    // Setup Dual EC with progression parameters
    dual_ec_setup(&state, opts->ratio, opts->base, opts->modulus, 
                  opts->base, opts->ratio);
    
    printf("Setup Parameters:\n");
    printf("  Generator:   %lu\n", opts->ratio);
    printf("  Multiplier:  %lu\n", opts->base);
    printf("  Field Mod:   %lu\n", opts->modulus);
    printf("\n");
    
    // Generate sample outputs
    printf("Sample Outputs:\n");
    for (int i = 0; i < 5; i++) {
        mpz_t output;
        mpz_init(output);
        
        if (dual_ec_generate(&state, output)) {
            gmp_printf("  Output %d:    %Zd\n", i+1, output);
        }
        
        mpz_clear(output);
    }
    printf("\n");
    
    // Analyze predictability
    mpfr_t predictability;
    mpfr_init2(predictability, opts->precision_bits);
    
    if (dual_ec_analyze_predictability(&state, 50, predictability)) {
        printf("Predictability Analysis:\n");
        mpfr_printf("  Score: %.6Rf (lower = more predictable)\n", predictability);
        
        double pred_val = mpfr_get_d(predictability, MPFR_RNDN);
        if (pred_val < 0.1) {
            printf("  ⚠️  High predictability detected - potential vulnerability\n");
        } else if (pred_val < 0.3) {
            printf("  ⚠️  Moderate predictability - requires further analysis\n");
        } else {
            printf("  ✅ Low predictability - appears secure\n");
        }
    }
    printf("\n");
    
    // Test for backdoors
    bool backdoor_detected;
    mpfr_t confidence;
    mpfr_init2(confidence, opts->precision_bits);
    
    if (dual_ec_backdoor_test(&state, &backdoor_detected, confidence)) {
        printf("Backdoor Analysis:\n");
        printf("  Backdoor Detected: %s\n", backdoor_detected ? "Yes" : "No");
        mpfr_printf("  Confidence:        %.2Rf\n", confidence);
    }
    
    mpfr_clear(predictability);
    mpfr_clear(confidence);
    dual_ec_clear(&state);
    printf("\n");
}

void analyze_sha256_bounds(const program_options_t *opts) {
    printf("🔒 SHA-256 Constant Bounds Analysis\n");
    printf("==================================\n");
    
    mod_geom_prog_t prog;
    mod_geom_prog_init(&prog);
    mod_geom_prog_set(&prog, opts->base, opts->ratio, opts->modulus, 64);
    
    // Test constants against progression bounds
    int constants_in_bounds = sha256_test_constant_bounds(&prog, 0.1); // 10% tolerance
    printf("Constants within bounds: %d/64 (%.1f%%)\n", 
           constants_in_bounds, (constants_in_bounds / 64.0) * 100);
    
    // Analyze geometric structure
    mpfr_t structure_score;
    mpfr_init2(structure_score, opts->precision_bits);
    
    if (sha256_analyze_geometric_structure(structure_score, &prog, opts->kappa_geo)) {
        printf("Geometric structure score: ");
        mpfr_printf("%.4Rf", structure_score);
        printf(" (higher = better fit)\n");
    }
    
    // Compute cryptographic strength bounds
    mpfr_t min_strength, max_strength;
    mpfr_init2(min_strength, opts->precision_bits);
    mpfr_init2(max_strength, opts->precision_bits);
    
    if (sha256_crypto_strength_bounds(min_strength, max_strength, &prog)) {
        printf("Cryptographic strength bounds:\n");
        mpfr_printf("  Minimum: %.2Rf bits\n", min_strength);
        mpfr_printf("  Maximum: %.2Rf bits\n", max_strength);
    }
    
    // Show sample bounds for first few constants
    if (opts->verbose) {
        printf("\nSample Constant Bounds (first 8 rounds):\n");
        for (int i = 0; i < 8; i++) {
            mpfr_t lower, upper;
            mpfr_init2(lower, opts->precision_bits);
            mpfr_init2(upper, opts->precision_bits);
            
            if (sha256_analyze_round_constant(lower, upper, i, &prog)) {
                printf("  K[%2d]: ", i);
                mpfr_printf("[%.0Rf, %.0Rf]", lower, upper);
                printf(" (actual: 0x%08x)\n", SHA256_ROUND_CONSTANTS[i]);
            }
            
            mpfr_clear(lower);
            mpfr_clear(upper);
        }
    }
    
    mpfr_clear(structure_score);
    mpfr_clear(min_strength);
    mpfr_clear(max_strength);
    mod_geom_prog_clear(&prog);
    printf("\n");
}

void analyze_crypto_strength(const program_options_t *opts) {
    printf("🛡️  Cryptographic Strength Analysis\n");
    printf("===================================\n");
    
    crypto_analysis_t analysis;
    crypto_analysis_init(&analysis);
    
    // Set up analysis with progression parameters
    mod_geom_prog_set(&analysis.progression, opts->base, opts->ratio, 
                      opts->modulus, opts->terms);
    mpfr_set_d(analysis.kappa_crypto, KAPPA_STAR_DEFAULT, MPFR_RNDN);
    analysis.rounds = 100;
    
    // Analyze overall strength
    mpfr_t security_estimate;
    mpfr_init2(security_estimate, opts->precision_bits);
    
    if (crypto_analyze_strength(&analysis, security_estimate)) {
        printf("Security Analysis:\n");
        mpfr_printf("  Overall strength estimate: %.2Rf bits\n", security_estimate);
        
        double strength = mpfr_get_d(security_estimate, MPFR_RNDN);
        if (strength >= 256) {
            printf("  🔐 Excellent security level\n");
        } else if (strength >= 128) {
            printf("  ✅ Good security level\n");
        } else if (strength >= 80) {
            printf("  ⚠️  Moderate security level\n");
        } else {
            printf("  ❌ Weak security level\n");
        }
    }
    
    // Validate parameters
    bool is_secure = crypto_validate_security(&analysis.progression, 128);
    printf("Parameter validation: %s\n", is_secure ? "✅ Secure" : "❌ Insecure");
    
    // Compute geodesic bounds
    mpfr_t lower_bound, upper_bound;
    mpfr_init2(lower_bound, opts->precision_bits);
    mpfr_init2(upper_bound, opts->precision_bits);
    
    crypto_geodesic_bounds(lower_bound, upper_bound, &analysis.progression, opts->kappa_geo);
    printf("Geodesic-enhanced bounds:\n");
    mpfr_printf("  Lower: %.2Rf bits\n", lower_bound);
    mpfr_printf("  Upper: %.2Rf bits\n", upper_bound);
    
    mpfr_clear(security_estimate);
    mpfr_clear(lower_bound);
    mpfr_clear(upper_bound);
    crypto_analysis_clear(&analysis);
    printf("\n");
}

void generate_terms(const program_options_t *opts) {
    printf("📈 Generated Progression Terms\n");
    printf("=============================\n");
    
    mod_geom_prog_t prog;
    mod_geom_prog_init(&prog);
    mod_geom_prog_set(&prog, opts->base, opts->ratio, opts->modulus, opts->generate_terms);
    
    printf("First %d terms of progression a·rⁿ (mod m):\n", opts->generate_terms);
    
    for (int i = 0; i < opts->generate_terms && i < 20; i++) {
        mpz_t term;
        mpz_init(term);
        
        mod_geom_prog_term(term, &prog, i);
        gmp_printf("  Term[%2d]: %Zd\n", i, term);
        
        if (opts->verbose && opts->kappa_geo != KAPPA_GEO_DEFAULT) {
            // Show geodesic enhancement
            mpfr_t geo_term;
            mpfr_init2(geo_term, opts->precision_bits);
            mod_geom_prog_geodesic_term(geo_term, &prog, i, opts->kappa_geo);
            mpfr_printf("             (geodesic: %.4Rf)\n", geo_term);
            mpfr_clear(geo_term);
        }
        
        mpz_clear(term);
    }
    
    if (opts->generate_terms > 20) {
        printf("  ... (showing first 20 of %d terms)\n", opts->generate_terms);
    }
    
    mod_geom_prog_clear(&prog);
    printf("\n");
}

void analyze_period(const program_options_t *opts) {
    printf("🔄 Period Analysis\n");
    printf("=================\n");
    
    mod_geom_prog_t prog;
    mod_geom_prog_init(&prog);
    mod_geom_prog_set(&prog, opts->base, opts->ratio, opts->modulus, 1000);
    
    unsigned long period = mod_geom_prog_period(&prog);
    
    printf("Progression period analysis:\n");
    if (period == 0) {
        printf("  Period: > 10000 (very long or infinite)\n");
        printf("  🔐 Excellent for cryptographic applications\n");
    } else {
        printf("  Period: %lu\n", period);
        printf("  Period bits: ~%.2f\n", log2(period));
        
        if (period >= 1000000) {
            printf("  🔐 Excellent period length\n");
        } else if (period >= 10000) {
            printf("  ✅ Good period length\n");
        } else if (period >= 1000) {
            printf("  ⚠️  Moderate period length\n");
        } else {
            printf("  ❌ Short period - cryptographically weak\n");
        }
    }
    
    // Compute sum of first period terms
    if (period > 0 && period < 1000) {
        mpz_t sum;
        mpz_init(sum);
        mod_geom_prog_sum(sum, &prog, period);
        gmp_printf("  Sum of first %lu terms: %Zd\n", period, sum);
        mpz_clear(sum);
    }
    
    mod_geom_prog_clear(&prog);
    printf("\n");
}

void validate_framework(const program_options_t *opts) {
    printf("✅ Z Framework Validation\n");
    printf("========================\n");
    
    printf("Parameter validation:\n");
    printf("  κ_geo = %.6f %s\n", opts->kappa_geo, 
           (opts->kappa_geo >= 0.05 && opts->kappa_geo <= 10.0) ? "✅" : "❌");
    printf("  Precision = %u bits %s\n", opts->precision_bits,
           (opts->precision_bits >= 256) ? "✅" : "⚠️");
    
    printf("  Base = %lu %s\n", opts->base, (opts->base >= 2) ? "✅" : "❌");
    printf("  Ratio = %lu %s\n", opts->ratio, (opts->ratio >= 2) ? "✅" : "❌");
    printf("  Modulus = %lu %s\n", opts->modulus, (opts->modulus >= opts->ratio) ? "✅" : "❌");
    
    // Test geodesic enhancement
    mod_geom_prog_t prog;
    mod_geom_prog_init(&prog);
    mod_geom_prog_set(&prog, opts->base, opts->ratio, opts->modulus, 10);
    
    mpfr_t regular_term, geodesic_term, enhancement_ratio;
    mpfr_init2(regular_term, opts->precision_bits);
    mpfr_init2(geodesic_term, opts->precision_bits);
    mpfr_init2(enhancement_ratio, opts->precision_bits);
    
    // Compare regular vs geodesic enhanced terms
    mpz_t term;
    mpz_init(term);
    mod_geom_prog_term(term, &prog, 5);
    mpfr_set_z(regular_term, term, MPFR_RNDN);
    
    mod_geom_prog_geodesic_term(geodesic_term, &prog, 5, opts->kappa_geo);
    
    if (!mpfr_zero_p(regular_term)) {
        mpfr_div(enhancement_ratio, geodesic_term, regular_term, MPFR_RNDN);
        printf("\nGeodetic enhancement validation:\n");
        mpfr_printf("  Enhancement ratio: %.4Rf\n", enhancement_ratio);
        printf("  Geodetic mapping: %s\n", 
               (!mpfr_equal_p(regular_term, geodesic_term)) ? "✅ Active" : "⚠️  Minimal");
    }
    
    mpz_clear(term);
    mpfr_clear(regular_term);
    mpfr_clear(geodesic_term);
    mpfr_clear(enhancement_ratio);
    mod_geom_prog_clear(&prog);
    printf("\n");
}

int main(int argc, char *argv[]) {
    program_options_t opts = {
        .base = 3,
        .ratio = 7,
        .modulus = 1024,
        .terms = 10,
        .analyze_dual_ec = false,
        .analyze_sha256 = false,
        .analyze_crypto_strength = false,
        .generate_terms = 0,
        .analyze_period = false,
        .kappa_geo = KAPPA_GEO_DEFAULT,
        .precision_bits = MP_DPS,
        .verbose = false,
        .validate = false,
        .output_file = NULL
    };
    
    int opt;
    int option_index = 0;
    
    while ((opt = getopt_long(argc, argv, "p:dscg:PG:r:vo:Vh", 
                              long_options, &option_index)) != -1) {
        switch (opt) {
            case 'p':
                if (!parse_progression_params(optarg, &opts)) {
                    return 1;
                }
                break;
            case 'd':
                opts.analyze_dual_ec = true;
                break;
            case 's':
                opts.analyze_sha256 = true;
                break;
            case 'c':
                opts.analyze_crypto_strength = true;
                break;
            case 'g':
                opts.generate_terms = atoi(optarg);
                if (opts.generate_terms <= 0) {
                    printf("❌ Error: Invalid number of terms\n");
                    return 1;
                }
                break;
            case 'P':
                opts.analyze_period = true;
                break;
            case 'G':
                opts.kappa_geo = atof(optarg);
                if (opts.kappa_geo <= 0) {
                    printf("❌ Error: Invalid geodesic parameter\n");
                    return 1;
                }
                break;
            case 'r':
                opts.precision_bits = atoi(optarg);
                if (opts.precision_bits < 64) {
                    printf("❌ Error: Precision must be at least 64 bits\n");
                    return 1;
                }
                break;
            case 'v':
                opts.verbose = true;
                break;
            case 'o':
                opts.output_file = malloc(strlen(optarg) + 1);
                strcpy(opts.output_file, optarg);
                break;
            case 'V':
                opts.validate = true;
                break;
            case 'h':
                print_help(argv[0]);
                return 0;
            default:
                print_help(argv[0]);
                return 1;
        }
    }
    
    // Set MPFR precision
    mpfr_set_default_prec(opts.precision_bits);
    
    printf("🔬 Modular Geometric Progressions in Cryptographic Analysis\n");
    printf("===========================================================\n\n");
    
    print_progression_info(&opts);
    
    // Execute requested analyses
    if (opts.generate_terms > 0) {
        generate_terms(&opts);
    }
    
    if (opts.analyze_period) {
        analyze_period(&opts);
    }
    
    if (opts.analyze_dual_ec) {
        analyze_dual_ec(&opts);
    }
    
    if (opts.analyze_sha256) {
        analyze_sha256_bounds(&opts);
    }
    
    if (opts.analyze_crypto_strength) {
        analyze_crypto_strength(&opts);
    }
    
    if (opts.validate) {
        validate_framework(&opts);
    }
    
    // Default demonstration if no specific analysis requested
    if (!opts.analyze_dual_ec && !opts.analyze_sha256 && !opts.analyze_crypto_strength &&
        opts.generate_terms == 0 && !opts.analyze_period && !opts.validate) {
        printf("💡 No specific analysis requested. Running basic demonstration...\n\n");
        opts.generate_terms = 5;
        generate_terms(&opts);
        opts.analyze_period = true;
        analyze_period(&opts);
    }
    
    printf("🎯 Analysis complete. Z Framework cryptographic analysis finished.\n");
    
    // Cleanup
    if (opts.output_file) {
        free(opts.output_file);
    }
    
    return 0;
}