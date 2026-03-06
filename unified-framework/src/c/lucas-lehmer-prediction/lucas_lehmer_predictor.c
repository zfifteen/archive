/**
 * @file lucas_lehmer_predictor.c
 * @brief Lucas-Lehmer Convergence Predictor - Main Program
 * @author Unified Framework Team
 * @version 1.0
 *
 * Main program implementation for Lucas-Lehmer Test with convergence prediction.
 * Provides command-line interface for testing Mersenne prime candidates with
 * early termination based on ℚ(√3) field analysis.
 */

#include "lucas_lehmer_predictor.h"
#include <getopt.h>
#include <sys/time.h>
#include <math.h>

// String handling compatibility
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <string.h>

// Simple strdup implementation for compatibility
char* local_strdup(const char* s) {
    size_t len = strlen(s) + 1;
    char* copy = malloc(len);
    if (copy) {
        memcpy(copy, s, len);
    }
    return copy;
}

// Known Mersenne primes for validation
const uint32_t KNOWN_MERSENNE_PRIMES[] = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281,
    3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209
};
const uint32_t NUM_KNOWN_MERSENNE_PRIMES = sizeof(KNOWN_MERSENNE_PRIMES) / sizeof(KNOWN_MERSENNE_PRIMES[0]);

int main(int argc, char *argv[]) {
    program_config_t config;
    init_program_config(&config);
    
    // Parse command line arguments
    int parse_result = parse_command_line(argc, argv, &config);
    if (parse_result != 0) {
        cleanup_program_config(&config);
        return parse_result;
    }
    
    print_header();
    
    int result = 0;
    if (config.batch_mode) {
        result = test_batch_exponents(&config);
    } else if (config.num_exponents == 1) {
        result = test_single_exponent(config.exponents[0], &config);
    } else {
        printf("❌ Error: No exponents specified\n");
        print_usage(argv[0]);
        result = LLT_ERROR_INVALID_ARGS;
    }
    
    cleanup_program_config(&config);
    return result;
}

void print_usage(const char *program_name) {
    printf("Usage: %s [OPTIONS] EXPONENT\n", program_name);
    printf("       %s [OPTIONS] --batch EXPONENT1,EXPONENT2,...\n", program_name);
    printf("\n");
    printf("Lucas-Lehmer Convergence Predictor\n");
    printf("Tests Mersenne prime candidates with early termination optimization\n");
    printf("\n");
    printf("OPTIONS:\n");
    printf("  -v, --verbose              Enable verbose output\n");
    printf("  -b, --batch LIST           Test multiple exponents (comma-separated)\n");
    printf("  -t, --threshold THRESHOLD  Set convergence threshold (default: 0.15)\n");
    printf("  -w, --window SIZE          Set pattern window size (default: 10)\n");
    printf("  -m, --min-iterations N     Minimum iterations before prediction (default: 5)\n");
    printf("  -n, --no-prediction        Disable early termination prediction\n");
    printf("  -s, --statistics           Show detailed statistics\n");
    printf("  -o, --output FILE          Save results to file\n");
    printf("  --benchmark                Run benchmark against standard LLT\n");
    printf("  --version                  Show version information\n");
    printf("  -h, --help                 Show this help message\n");
    printf("\n");
    printf("EXAMPLES:\n");
    printf("  %s 2203                    # Test 2^2203 - 1\n", program_name);
    printf("  %s -v --statistics 607     # Verbose test with statistics\n", program_name);
    printf("  %s -b 607,1279,2203        # Batch test multiple candidates\n", program_name);
    printf("  %s --benchmark 1279        # Benchmark prediction vs standard\n", program_name);
    printf("\n");
    printf("Known Mersenne primes: 2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127,\n");
    printf("                      521, 607, 1279, 2203, 2281, 3217, 4253, 4423...\n");
}

void print_version(void) {
    printf("Lucas-Lehmer Convergence Predictor v%s\n", LLT_PREDICTOR_VERSION_STRING);
#if LLT_HAVE_MPFR
    printf("Built with MPFR %s, precision: %d bits\n", mpfr_get_version(), LLT_PRECISION_BITS);
#else
    printf("Built with fallback precision (double), limited to ~15 decimal digits\n");
#endif
    printf("Convergence prediction based on ℚ(√3) field analysis\n");
}

void print_header(void) {
    printf("╔═══════════════════════════════════════════════════════════════════╗\n");
    printf("║              Lucas-Lehmer Convergence Predictor v%s               ║\n", LLT_PREDICTOR_VERSION_STRING);
    printf("║                                                                   ║\n");
    printf("║  Optimized Mersenne prime testing with early termination         ║\n");
    printf("║  Based on ℚ(√3) field analysis and statistical pattern matching  ║\n");
    printf("║                                                                   ║\n");
    printf("║  S_n ≈ (2 + √3)^{2^n} + (2 - √3)^{2^n}                          ║\n");
    printf("║  Early termination when S_i mod M_p deviates from patterns       ║\n");
    printf("╚═══════════════════════════════════════════════════════════════════╝\n");
    printf("\n");
}

void init_program_config(program_config_t *config) {
    memset(config, 0, sizeof(program_config_t));
    
    // Set default values
    config->batch_mode = false;
    config->verbose = false;
    config->benchmark_mode = false;
    config->show_statistics = false;
    config->save_results = false;
    config->output_file = NULL;
    config->exponents = NULL;
    config->num_exponents = 0;
    
    // Initialize prediction configuration with defaults
    config->prediction_config.early_termination_enabled = true;
    config->prediction_config.convergence_threshold = CONVERGENCE_THRESHOLD;
    config->prediction_config.pattern_window_size = PATTERN_WINDOW_SIZE;
    config->prediction_config.min_iterations_before_check = MIN_ITERATIONS_BEFORE_CHECK;
    config->prediction_config.verbose_output = false;
}

void cleanup_program_config(program_config_t *config) {
    if (config->exponents) {
        free(config->exponents);
    }
    if (config->output_file) {
        free(config->output_file);
    }
}

int parse_command_line(int argc, char *argv[], program_config_t *config) {
    static struct option long_options[] = {
        {"verbose",         no_argument,       0, 'v'},
        {"batch",           required_argument, 0, 'b'},
        {"threshold",       required_argument, 0, 't'},
        {"window",          required_argument, 0, 'w'},
        {"min-iterations",  required_argument, 0, 'm'},
        {"no-prediction",   no_argument,       0, 'n'},
        {"statistics",      no_argument,       0, 's'},
        {"output",          required_argument, 0, 'o'},
        {"benchmark",       no_argument,       0, 0},
        {"version",         no_argument,       0, 0},
        {"help",            no_argument,       0, 'h'},
        {0, 0, 0, 0}
    };
    
    int option_index = 0;
    int c;
    
    while ((c = getopt_long(argc, argv, "vb:t:w:m:nso:h", long_options, &option_index)) != -1) {
        switch (c) {
            case 'v':
                config->verbose = true;
                config->prediction_config.verbose_output = true;
                break;
                
            case 'b':
                config->batch_mode = true;
                if (parse_exponent_list(optarg, &config->exponents, &config->num_exponents) != 0) {
                    printf("❌ Error: Invalid exponent list format\n");
                    return LLT_ERROR_INVALID_ARGS;
                }
                break;
                
            case 't':
                config->prediction_config.convergence_threshold = strtod(optarg, NULL);
                if (config->prediction_config.convergence_threshold <= 0.0 || 
                    config->prediction_config.convergence_threshold >= 1.0) {
                    printf("❌ Error: Threshold must be between 0 and 1\n");
                    return LLT_ERROR_INVALID_ARGS;
                }
                break;
                
            case 'w':
                config->prediction_config.pattern_window_size = (uint32_t)strtoul(optarg, NULL, 10);
                if (config->prediction_config.pattern_window_size < 2 || 
                    config->prediction_config.pattern_window_size > 100) {
                    printf("❌ Error: Window size must be between 2 and 100\n");
                    return LLT_ERROR_INVALID_ARGS;
                }
                break;
                
            case 'm':
                config->prediction_config.min_iterations_before_check = (uint32_t)strtoul(optarg, NULL, 10);
                break;
                
            case 'n':
                config->prediction_config.early_termination_enabled = false;
                break;
                
            case 's':
                config->show_statistics = true;
                break;
                
            case 'o':
                config->save_results = true;
                config->output_file = local_strdup(optarg);
                break;
                
            case 0:
                if (strcmp(long_options[option_index].name, "benchmark") == 0) {
                    config->benchmark_mode = true;
                } else if (strcmp(long_options[option_index].name, "version") == 0) {
                    print_version();
                    return 1;
                }
                break;
                
            case 'h':
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    
    // Parse remaining arguments as exponents
    if (!config->batch_mode && optind < argc) {
        config->num_exponents = argc - optind;
        config->exponents = malloc(config->num_exponents * sizeof(uint32_t));
        
        for (uint32_t i = 0; i < config->num_exponents; i++) {
            uint32_t exponent = (uint32_t)strtoul(argv[optind + i], NULL, 10);
            if (!validate_exponent(exponent)) {
                printf("❌ Error: Invalid exponent %u\n", exponent);
                return LLT_ERROR_INVALID_EXPONENT;
            }
            config->exponents[i] = exponent;
        }
    }
    
    return 0;
}

int parse_exponent_list(const char *list_str, uint32_t **exponents, uint32_t *count) {
    char *str_copy = local_strdup(list_str);
    char *token;
    uint32_t capacity = 10;
    
    *exponents = malloc(capacity * sizeof(uint32_t));
    *count = 0;
    
    token = strtok(str_copy, ",");
    while (token != NULL) {
        uint32_t exponent = (uint32_t)strtoul(token, NULL, 10);
        if (!validate_exponent(exponent)) {
            free(str_copy);
            free(*exponents);
            return -1;
        }
        
        if (*count >= capacity) {
            capacity *= 2;
            *exponents = realloc(*exponents, capacity * sizeof(uint32_t));
        }
        
        (*exponents)[*count] = exponent;
        (*count)++;
        
        token = strtok(NULL, ",");
    }
    
    free(str_copy);
    return 0;
}

int test_single_exponent(uint32_t exponent, const program_config_t *config) {
    printf("🔬 Testing Mersenne candidate: 2^%u - 1\n", exponent);
    printf("   Exponent: %u\n", exponent);
    printf("   Known prime: %s\n", is_known_mersenne_prime(exponent) ? "Yes" : "No");
    printf("   Early termination: %s\n", 
           config->prediction_config.early_termination_enabled ? "Enabled" : "Disabled");
    printf("\n");
    
    llt_prediction_result_t result;
    double start_time = get_current_time_ms();
    
    int status = lucas_lehmer_with_prediction(exponent, &config->prediction_config, &result);
    
    double end_time = get_current_time_ms();
    double elapsed_time = end_time - start_time;
    
    if (status != 0) {
        printf("❌ Error: Computation failed (code: %d)\n", status);
        return status;
    }
    
    print_test_result(exponent, &result, config);
    
    printf("\n⏱️  Execution time: %.2f ms\n", elapsed_time);
    
    if (config->benchmark_mode) {
        benchmark_result_t benchmark;
        benchmark_exponent(exponent, config, &benchmark);
        print_benchmark_result(&benchmark);
    }
    
    return 0;
}

int test_batch_exponents(const program_config_t *config) {
    printf("🔄 Batch testing %u Mersenne candidates...\n\n", config->num_exponents);
    
    llt_prediction_result_t *results = malloc(config->num_exponents * sizeof(llt_prediction_result_t));
    
    for (uint32_t i = 0; i < config->num_exponents; i++) {
        uint32_t exponent = config->exponents[i];
        
        printf("📊 [%u/%u] Testing 2^%u - 1...\n", i + 1, config->num_exponents, exponent);
        
        double start_time = get_current_time_ms();
        int status = lucas_lehmer_with_prediction(exponent, &config->prediction_config, &results[i]);
        double end_time = get_current_time_ms();
        
        if (status == 0) {
            printf("   Result: %s", results[i].is_prime ? "PRIME" : "COMPOSITE");
            if (results[i].early_termination_triggered) {
                printf(" (early termination, %.1f%% saved)", results[i].efficiency_gain);
            }
            printf(" [%.2f ms]\n", end_time - start_time);
        } else {
            printf("   ❌ Error (code: %d)\n", status);
        }
        
        if (config->verbose && i < config->num_exponents - 1) {
            printf("\n");
        }
    }
    
    print_batch_summary(results, config->num_exponents);
    
    if (config->save_results) {
        save_results_to_file(config->output_file, results, config->exponents, config->num_exponents);
    }
    
    free(results);
    return 0;
}

int benchmark_exponent(uint32_t exponent, const program_config_t *config, 
                      benchmark_result_t *result) {
    
    result->exponent = exponent;
    
    // Standard Lucas-Lehmer test
    double start_time = get_current_time_ms();
    bool standard_result = standard_lucas_lehmer_test(exponent, &result->standard_iterations);
    result->time_standard = get_current_time_ms() - start_time;
    
    // Prediction-enhanced test
    llt_prediction_result_t prediction_result;
    start_time = get_current_time_ms();
    lucas_lehmer_with_prediction(exponent, &config->prediction_config, &prediction_result);
    result->time_predicted = get_current_time_ms() - start_time;
    
    result->predicted_iterations = prediction_result.iterations_performed;
    result->efficiency_gain = prediction_result.efficiency_gain;
    result->correct_prediction = (standard_result == prediction_result.is_prime);
    
    return 0;
}

bool standard_lucas_lehmer_test(uint32_t exponent, uint32_t *iterations_performed) {
    mpfr_t s, mersenne, temp;
    mpfr_init2(&s, LLT_PRECISION_BITS);
    mpfr_init2(&mersenne, LLT_PRECISION_BITS);
    mpfr_init2(&temp, LLT_PRECISION_BITS);
    
    // Calculate 2^p - 1
    mpfr_ui_pow_ui(&mersenne, 2, exponent, MPFR_RNDN);
    mpfr_sub_ui(&mersenne, &mersenne, 1, MPFR_RNDN);
    
    // S_0 = 4
    mpfr_set_ui(&s, 4, MPFR_RNDN);
    
    // Iterate: S_{i+1} = S_i^2 - 2 mod (2^p - 1)
    for (uint32_t i = 1; i < exponent - 1; i++) {
        mpfr_sqr(&temp, &s, MPFR_RNDN);
        mpfr_sub_ui(&s, &temp, 2, MPFR_RNDN);
        mpfr_fmod(&s, &s, &mersenne, MPFR_RNDN);
    }
    
    *iterations_performed = exponent - 1;
    bool is_prime = mpfr_zero_p(&s);
    
    mpfr_clear(&s);
    mpfr_clear(&mersenne);
    mpfr_clear(&temp);
    
    return is_prime;
}

void print_test_result(uint32_t exponent, const llt_prediction_result_t *result,
                      const program_config_t *config) {
    
    printf("📋 RESULT SUMMARY\n");
    printf("================\n");
    printf("🔢 Mersenne candidate: 2^%u - 1\n", exponent);
    printf("🎯 Result: %s%s\n", 
           result->is_prime ? "✅ PRIME" : "❌ COMPOSITE",
           is_known_mersenne_prime(exponent) ? " (verified)" : "");
    
    printf("⚙️  Iterations performed: %u", result->iterations_performed);
    if (result->iterations_saved > 0) {
        printf(" (saved: %u, %.1f%% efficiency gain)", 
               result->iterations_saved, result->efficiency_gain);
    }
    printf("\n");
    
    if (result->early_termination_triggered) {
        printf("⚡ Early termination triggered by convergence prediction\n");
    }
    
    if (config->show_statistics) {
        printf("\n");
        print_convergence_stats(&result->stats);
    }
}

void print_benchmark_result(const benchmark_result_t *result) {
    printf("\n🏁 BENCHMARK RESULTS\n");
    printf("===================\n");
    printf("Standard LLT:    %u iterations, %.2f ms\n", 
           result->standard_iterations, result->time_standard);
    printf("With prediction: %u iterations, %.2f ms\n", 
           result->predicted_iterations, result->time_predicted);
    
    if (result->efficiency_gain > 0) {
        printf("Efficiency gain: %.1f%% iterations, %.1f%% time\n",
               result->efficiency_gain,
               100.0 * (result->time_standard - result->time_predicted) / result->time_standard);
    }
    
    printf("Accuracy: %s\n", result->correct_prediction ? "✅ Correct" : "❌ Incorrect");
}

void print_batch_summary(const llt_prediction_result_t *results, uint32_t count) {
    printf("\n📊 BATCH SUMMARY\n");
    printf("===============\n");
    
    uint32_t total_primes = 0;
    uint32_t total_early_terminations = 0;
    uint32_t total_iterations_saved = 0;
    
    for (uint32_t i = 0; i < count; i++) {
        if (results[i].is_prime) total_primes++;
        if (results[i].early_termination_triggered) total_early_terminations++;
        total_iterations_saved += results[i].iterations_saved;
    }
    
    printf("Total candidates tested: %u\n", count);
    printf("Primes found: %u\n", total_primes);
    printf("Early terminations: %u (%.1f%%)\n", 
           total_early_terminations, 100.0 * total_early_terminations / count);
    printf("Total iterations saved: %u\n", total_iterations_saved);
}

void save_results_to_file(const char *filename, const llt_prediction_result_t *results,
                         const uint32_t *exponents, uint32_t count) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        printf("❌ Error: Cannot open file %s for writing\n", filename);
        return;
    }
    
    fprintf(file, "# Lucas-Lehmer Convergence Prediction Results\n");
    fprintf(file, "# Exponent,Prime,Iterations,Saved,EarlyTermination,EfficiencyGain\n");
    
    for (uint32_t i = 0; i < count; i++) {
        fprintf(file, "%u,%s,%u,%u,%s,%.2f\n",
                exponents[i],
                results[i].is_prime ? "true" : "false",
                results[i].iterations_performed,
                results[i].iterations_saved,
                results[i].early_termination_triggered ? "true" : "false",
                results[i].efficiency_gain);
    }
    
    fclose(file);
    printf("📁 Results saved to: %s\n", filename);
}

double get_current_time_ms(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0;
}

const char *format_large_number(uint32_t exponent) {
    static char buffer[64];
    // Approximate number of digits in 2^p - 1
    uint32_t digits = (uint32_t)(exponent * log10(2));
    
    if (digits >= 1000000) {
        snprintf(buffer, sizeof(buffer), "~%.1fM digits", digits / 1000000.0);
    } else if (digits >= 1000) {
        snprintf(buffer, sizeof(buffer), "~%.1fK digits", digits / 1000.0);
    } else {
        snprintf(buffer, sizeof(buffer), "%u digits", digits);
    }
    
    return buffer;
}

void print_progress_bar(uint32_t current, uint32_t total) {
    const int bar_width = 40;
    int progress = (int)(((double)current / total) * bar_width);
    
    printf("\r[");
    for (int i = 0; i < bar_width; i++) {
        if (i < progress) printf("█");
        else printf("░");
    }
    printf("] %u/%u", current, total);
    fflush(stdout);
}

bool validate_exponent(uint32_t exponent) {
    // Basic validation: exponent must be >= 2 and reasonable size
    if (exponent < 2) return false;
    if (exponent > 100000) return false;  // Prevent extremely large computations
    
    // For very efficient testing, we could require exponent to be prime,
    // but this implementation allows any exponent for educational purposes
    return true;
}