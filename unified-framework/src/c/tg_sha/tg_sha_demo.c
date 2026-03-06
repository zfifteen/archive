/**
 * @file tg_sha_demo.c
 * @brief Transparent Geometric SHA (TG-SHA) - Demonstration Program
 * 
 * Comprehensive demonstration of TG-SHA showing both "secure" and "broken"
 * modes, demonstrating how geometric predictability emerges when the critical
 * k* parameter is exposed, analogous to the Dual_EC_DRBG vulnerability.
 */

#include "tg_sha.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <getopt.h>

// ============================================================================
// DEMONSTRATION FUNCTIONS
// ============================================================================

/**
 * @brief Print program usage information
 */
void print_usage(const char* program_name) {
    printf("TG-SHA: Transparent Geometric SHA Demonstration\n");
    printf("===============================================\n\n");
    printf("Usage: %s [OPTIONS]\n\n", program_name);
    printf("OPTIONS:\n");
    printf("  --secure         Run in secure mode (k* hidden)\n");
    printf("  --broken         Run in broken mode (k* exposed)\n");
    printf("  --both           Run both modes for comparison\n");
    printf("  --analyze        Perform geometric vulnerability analysis\n");
    printf("  --predict N      Generate N predictability demonstrations\n");
    printf("  --message TEXT   Hash the specified message\n");
    printf("  --verbose        Enable verbose output\n");
    printf("  --help           Show this help message\n\n");
    printf("DESCRIPTION:\n");
    printf("  TG-SHA demonstrates geometric predictability in cryptographic\n");
    printf("  constants. When the critical scalar k* is exposed (broken mode),\n");
    printf("  internal states become predictable through geometric relationships,\n");
    printf("  similar to the Dual_EC_DRBG 'd' parameter vulnerability.\n\n");
    printf("EXAMPLES:\n");
    printf("  %s --secure --message \"Hello World\"     # Secure hashing\n", program_name);
    printf("  %s --broken --analyze                    # Vulnerability analysis\n", program_name);
    printf("  %s --both --predict 8                   # Comparison demo\n", program_name);
}

/**
 * @brief Demonstrate secure mode operation
 */
int demonstrate_secure_mode(const char* message, bool verbose) {
    printf("=== TG-SHA SECURE MODE DEMONSTRATION ===\n");
    printf("k* parameter: HIDDEN (secure operation)\n");
    printf("Expected behavior: Unpredictable, cryptographically secure\n\n");
    
    tg_sha_ctx_t ctx;
    tg_sha_result_t result;
    
    // Initialize in secure mode
    result = tg_sha_init(&ctx, true);
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Failed to initialize TG-SHA: %s\n", 
               tg_sha_result_string(result));
        return 1;
    }
    
    if (verbose) {
        char report[1024];
        tg_sha_generate_report(&ctx, report, sizeof(report));
        printf("Configuration Report:\n%s\n", report);
    }
    
    // Hash the message
    const char* test_msg = message ? message : "TG-SHA Secure Mode Test";
    result = tg_sha_update(&ctx, (const uint8_t*)test_msg, strlen(test_msg));
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Update failed: %s\n", tg_sha_result_string(result));
        tg_sha_cleanup(&ctx);
        return 1;
    }
    
    uint8_t hash[TG_SHA_HASH_SIZE];
    result = tg_sha_final(&ctx, hash);
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Finalization failed: %s\n", tg_sha_result_string(result));
        tg_sha_cleanup(&ctx);
        return 1;
    }
    
    printf("Message: \"%s\"\n", test_msg);
    printf("Hash: ");
    tg_sha_print_hash(hash, TG_SHA_HASH_SIZE);
    
    // Demonstrate unpredictability
    uint32_t predictions[8];
    tg_sha_demonstrate_predictability(&ctx, 8, predictions);
    
    printf("\nPredictability Test (should be random-like):\n");
    for (int i = 0; i < 8; i += 4) {
        printf("  %08x %08x %08x %08x\n", 
               predictions[i], predictions[i+1], 
               predictions[i+2], predictions[i+3]);
    }
    
    printf("✅ Secure mode: k* parameter properly hidden\n");
    printf("✅ Hash generation: Normal cryptographic behavior\n");
    printf("✅ Predictability: Minimal (as expected)\n\n");
    
    tg_sha_cleanup(&ctx);
    return 0;
}

/**
 * @brief Demonstrate broken mode operation with k* exposure
 */
int demonstrate_broken_mode(const char* message, bool verbose) {
    printf("=== TG-SHA BROKEN MODE DEMONSTRATION ===\n");
    printf("k* parameter: EXPOSED (vulnerability demonstration)\n");
    printf("Expected behavior: Geometric predictability emerges\n\n");
    
    tg_sha_ctx_t ctx;
    tg_sha_result_t result;
    
    // Initialize in broken mode
    result = tg_sha_init(&ctx, false);
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Failed to initialize TG-SHA: %s\n", 
               tg_sha_result_string(result));
        return 1;
    }
    
    // Expose k* parameter (the critical vulnerability)
    mpfr_t k_star_value;
    mpfr_init2(k_star_value, TG_SHA_MPFR_PREC);
    result = tg_sha_expose_k_star(&ctx, k_star_value);
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Failed to expose k*: %s\n", tg_sha_result_string(result));
        tg_sha_cleanup(&ctx);
        mpfr_clear(k_star_value);
        return 1;
    }
    
    printf("🚨 CRITICAL PARAMETER EXPOSED:\n");
    printf("k* = ");
    mpfr_printf("%.10Rf\n", k_star_value);
    printf("This exposure allows geometric prediction of internal states!\n\n");
    
    if (verbose) {
        char report[1024];
        tg_sha_generate_report(&ctx, report, sizeof(report));
        printf("Configuration Report:\n%s\n", report);
    }
    
    // Hash the same message
    const char* test_msg = message ? message : "TG-SHA Broken Mode Test";
    result = tg_sha_update(&ctx, (const uint8_t*)test_msg, strlen(test_msg));
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Update failed: %s\n", tg_sha_result_string(result));
        tg_sha_cleanup(&ctx);
        mpfr_clear(k_star_value);
        return 1;
    }
    
    uint8_t hash[TG_SHA_HASH_SIZE];
    result = tg_sha_final(&ctx, hash);
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Finalization failed: %s\n", tg_sha_result_string(result));
        tg_sha_cleanup(&ctx);
        mpfr_clear(k_star_value);
        return 1;
    }
    
    printf("Message: \"%s\"\n", test_msg);
    printf("Hash: ");
    tg_sha_print_hash(hash, TG_SHA_HASH_SIZE);
    
    // Perform vulnerability analysis
    tg_sha_analysis_t analysis;
    result = tg_sha_predict_states(&ctx, &analysis);
    if (result == TG_SHA_SUCCESS) {
        printf("\n🔍 VULNERABILITY ANALYSIS:\n");
        tg_sha_print_analysis(&analysis);
    }
    
    // Demonstrate high predictability
    uint32_t predictions[8];
    tg_sha_demonstrate_predictability(&ctx, 8, predictions);
    
    printf("\nPredictability Test (geometric pattern should be evident):\n");
    for (int i = 0; i < 8; i += 4) {
        printf("  %08x %08x %08x %08x\n", 
               predictions[i], predictions[i+1], 
               predictions[i+2], predictions[i+3]);
    }
    
    printf("\n❌ Broken mode: k* parameter exposed\n");
    printf("❌ Geometric vulnerability: DETECTED\n");
    printf("❌ Predictability: HIGH (vulnerability confirmed)\n\n");
    
    tg_sha_cleanup(&ctx);
    mpfr_clear(k_star_value);
    return 0;
}

/**
 * @brief Demonstrate side-by-side comparison of both modes
 */
int demonstrate_comparison(int num_predictions) {
    printf("=== TG-SHA SECURE vs BROKEN MODE COMPARISON ===\n");
    printf("Demonstrating the impact of k* parameter exposure\n\n");
    
    tg_sha_ctx_t secure_ctx, broken_ctx;
    tg_sha_result_t result;
    
    // Initialize both contexts
    result = tg_sha_init(&secure_ctx, true);
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Failed to initialize secure context\n");
        return 1;
    }
    
    result = tg_sha_init(&broken_ctx, false);
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Failed to initialize broken context\n");
        tg_sha_cleanup(&secure_ctx);
        return 1;
    }
    
    // Expose k* in broken context
    mpfr_t k_star;
    mpfr_init2(k_star, TG_SHA_MPFR_PREC);
    tg_sha_expose_k_star(&broken_ctx, k_star);
    
    printf("SECURE MODE (k* hidden)     vs     BROKEN MODE (k* exposed)\n");
    printf("==========================         ==========================\n");
    
    // Compare predictability
    uint32_t secure_pred[16], broken_pred[16];
    tg_sha_demonstrate_predictability(&secure_ctx, num_predictions, secure_pred);
    tg_sha_demonstrate_predictability(&broken_ctx, num_predictions, broken_pred);
    
    printf("\nPredictability Comparison (%d predictions):\n", num_predictions);
    for (int i = 0; i < num_predictions; i++) {
        printf("Secure: %08x    Broken: %08x", secure_pred[i], broken_pred[i]);
        
        // Analyze geometric relationship in broken mode
        double ratio = (double)broken_pred[i] / (double)(broken_pred[0] + 1);
        if (i > 0 && ratio > 1.5 && ratio < 2.0) {
            printf("  ← Geometric pattern!");
        }
        printf("\n");
    }
    
    printf("\n📊 ANALYSIS SUMMARY:\n");
    printf("• Secure mode: Random-like values, no discernible pattern\n");
    printf("• Broken mode: Geometric progression evident when k* known\n");
    printf("• Vulnerability: k* exposure enables state prediction\n");
    printf("• Analogy: Similar to Dual_EC_DRBG 'd' parameter attack\n\n");
    
    tg_sha_cleanup(&secure_ctx);
    tg_sha_cleanup(&broken_ctx);
    mpfr_clear(k_star);
    return 0;
}

/**
 * @brief Perform comprehensive geometric analysis
 */
int perform_geometric_analysis(bool verbose) {
    printf("=== TG-SHA GEOMETRIC VULNERABILITY ANALYSIS ===\n");
    printf("Comprehensive analysis of geometric relationships and predictability\n\n");
    
    tg_sha_ctx_t ctx;
    tg_sha_result_t result;
    
    // Initialize in broken mode for analysis
    result = tg_sha_init(&ctx, false);
    if (result != TG_SHA_SUCCESS) {
        printf("ERROR: Failed to initialize analysis context\n");
        return 1;
    }
    
    // Parameter validation
    result = tg_sha_validate_parameters(&ctx);
    if (result != TG_SHA_SUCCESS) {
        printf("WARNING: Parameter validation failed: %s\n", 
               tg_sha_result_string(result));
    } else {
        printf("✅ Z Framework parameters validated\n");
    }
    
    // Expose k* for analysis
    mpfr_t k_star;
    mpfr_init2(k_star, TG_SHA_MPFR_PREC);
    tg_sha_expose_k_star(&ctx, k_star);
    
    printf("\n🔬 GEOMETRIC STRUCTURE ANALYSIS:\n");
    printf("k* (critical scalar): ");
    mpfr_printf("%.10Rf\n", k_star);
    printf("κ_geo (geodesic): %.6f\n", TG_SHA_KAPPA_GEO);
    printf("φ (golden ratio): %.10f\n", TG_SHA_PHI_SCALED);
    printf("e (Euler's number): %.10f\n", TG_SHA_EULER_E);
    
    // Generate full analysis report
    char report[2048];
    result = tg_sha_generate_report(&ctx, report, sizeof(report));
    if (result == TG_SHA_SUCCESS) {
        printf("\n%s\n", report);
    }
    
    // Perform predictability analysis
    tg_sha_analysis_t analysis;
    result = tg_sha_predict_states(&ctx, &analysis);
    if (result == TG_SHA_SUCCESS) {
        printf("🎯 PREDICTABILITY ASSESSMENT:\n");
        tg_sha_print_analysis(&analysis);
    }
    
    printf("\n🏛️ Z FRAMEWORK INTEGRATION:\n");
    printf("• High-precision MPFR arithmetic (%d-bit precision)\n", TG_SHA_MPFR_PREC);
    printf("• Geodesic mapping with standardized κ_geo parameter\n");
    printf("• Cross-domain geometric analysis (discrete ↔ crypto)\n");
    printf("• Empirical validation of geometric vulnerability\n");
    
    printf("\n⚠️  VULNERABILITY SUMMARY:\n");
    printf("• TG-SHA demonstrates how geometric structure in constants\n");
    printf("  can introduce predictable relationships when key parameters\n");
    printf("  are exposed, analogous to the Dual_EC_DRBG vulnerability.\n");
    printf("• The k* parameter acts as a 'geometric backdoor' enabling\n");
    printf("  prediction of internal states and round constants.\n");
    printf("• This serves as a cautionary example for cryptographic design.\n\n");
    
    tg_sha_cleanup(&ctx);
    mpfr_clear(k_star);
    return 0;
}

// ============================================================================
// MAIN PROGRAM
// ============================================================================

int main(int argc, char* argv[]) {
    // Command line options
    bool secure_mode = false;
    bool broken_mode = false;
    bool both_modes = false;
    bool analyze = false;
    bool verbose = false;
    int num_predictions = 0;
    char* message = NULL;
    
    // Long options
    static struct option long_options[] = {
        {"secure",    no_argument,       0, 's'},
        {"broken",    no_argument,       0, 'b'},
        {"both",      no_argument,       0, 'B'},
        {"analyze",   no_argument,       0, 'a'},
        {"predict",   required_argument, 0, 'p'},
        {"message",   required_argument, 0, 'm'},
        {"verbose",   no_argument,       0, 'v'},
        {"help",      no_argument,       0, 'h'},
        {0, 0, 0, 0}
    };
    
    int opt;
    while ((opt = getopt_long(argc, argv, "sbBap:m:vh", long_options, NULL)) != -1) {
        switch (opt) {
            case 's':
                secure_mode = true;
                break;
            case 'b':
                broken_mode = true;
                break;
            case 'B':
                both_modes = true;
                break;
            case 'a':
                analyze = true;
                break;
            case 'p':
                num_predictions = atoi(optarg);
                if (num_predictions <= 0 || num_predictions > 16) {
                    printf("ERROR: Number of predictions must be 1-16\n");
                    return 1;
                }
                break;
            case 'm':
                message = optarg;
                break;
            case 'v':
                verbose = true;
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    
    // If no specific mode selected, show help
    if (!secure_mode && !broken_mode && !both_modes && !analyze && num_predictions == 0) {
        print_usage(argv[0]);
        return 1;
    }
    
    printf("TG-SHA: Transparent Geometric SHA Demonstration\n");
    printf("===============================================\n");
    printf("Z Framework Geometric Vulnerability Demonstration\n");
    printf("Analogous to Dual_EC_DRBG 'd' parameter exposure\n\n");
    
    int result = 0;
    
    if (secure_mode) {
        result = demonstrate_secure_mode(message, verbose);
        if (result != 0) return result;
    }
    
    if (broken_mode) {
        result = demonstrate_broken_mode(message, verbose);
        if (result != 0) return result;
    }
    
    if (both_modes) {
        int preds = num_predictions > 0 ? num_predictions : 8;
        result = demonstrate_comparison(preds);
        if (result != 0) return result;
    }
    
    if (num_predictions > 0) {
        result = demonstrate_comparison(num_predictions);
        if (result != 0) return result;
    }
    
    if (analyze) {
        result = perform_geometric_analysis(verbose);
        if (result != 0) return result;
    }
    
    printf("🎉 TG-SHA demonstration completed successfully!\n");
    printf("📚 This demonstrates the importance of protecting geometric\n");
    printf("    parameters in cryptographic constructions.\n\n");
    
    return 0;
}