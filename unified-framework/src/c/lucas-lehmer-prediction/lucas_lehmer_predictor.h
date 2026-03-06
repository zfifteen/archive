/**
 * @file lucas_lehmer_predictor.h
 * @brief Lucas-Lehmer Convergence Predictor - Main Interface
 * @author Unified Framework Team
 * @version 1.0
 *
 * Main interface for Lucas-Lehmer Test with convergence prediction.
 * Provides optimized Mersenne prime testing with early termination
 * based on statistical pattern analysis in the ℚ(√3) field.
 */

#ifndef LUCAS_LEHMER_PREDICTOR_H
#define LUCAS_LEHMER_PREDICTOR_H

#include "llt_convergence.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#ifdef __cplusplus
extern "C" {
#endif

// Version information
#define LLT_PREDICTOR_VERSION_MAJOR 1
#define LLT_PREDICTOR_VERSION_MINOR 0
#define LLT_PREDICTOR_VERSION_PATCH 0
#define LLT_PREDICTOR_VERSION_STRING "1.0.0"

// Program configuration
typedef struct {
    bool batch_mode;              // Process multiple exponents
    bool verbose;                 // Verbose output
    bool benchmark_mode;          // Benchmark against standard LLT
    bool show_statistics;         // Show detailed statistics
    bool save_results;           // Save results to file
    char *output_file;           // Output file path
    uint32_t *exponents;         // Array of exponents to test
    uint32_t num_exponents;      // Number of exponents
    llt_prediction_config_t prediction_config; // Prediction configuration
} program_config_t;

// Benchmark results
typedef struct {
    uint32_t exponent;
    uint32_t standard_iterations;     // Standard LLT iterations
    uint32_t predicted_iterations;    // Iterations with prediction
    double time_standard;             // Time for standard LLT (ms)
    double time_predicted;            // Time with prediction (ms)
    double efficiency_gain;           // Efficiency improvement
    bool correct_prediction;          // Whether prediction was correct
} benchmark_result_t;

// Function declarations

// Main program functions
int main(int argc, char *argv[]);
void print_usage(const char *program_name);
void print_version(void);
void print_header(void);

// Configuration management
void init_program_config(program_config_t *config);
void cleanup_program_config(program_config_t *config);
int parse_command_line(int argc, char *argv[], program_config_t *config);
int parse_exponent_list(const char *list_str, uint32_t **exponents, uint32_t *count);

// Core testing functions
int test_single_exponent(uint32_t exponent, const program_config_t *config);
int test_batch_exponents(const program_config_t *config);
int benchmark_exponent(uint32_t exponent, const program_config_t *config, 
                      benchmark_result_t *result);

// Standard Lucas-Lehmer test (for comparison)
bool standard_lucas_lehmer_test(uint32_t exponent, uint32_t *iterations_performed);

// Output and reporting functions
void print_test_result(uint32_t exponent, const llt_prediction_result_t *result,
                      const program_config_t *config);
void print_benchmark_result(const benchmark_result_t *result);
void print_batch_summary(const llt_prediction_result_t *results, uint32_t count);
void save_results_to_file(const char *filename, const llt_prediction_result_t *results,
                         const uint32_t *exponents, uint32_t count);

// Utility functions
double get_current_time_ms(void);
const char *format_large_number(uint32_t exponent);
void print_progress_bar(uint32_t current, uint32_t total);
bool validate_exponent(uint32_t exponent);

// Known Mersenne primes (for validation)
extern const uint32_t KNOWN_MERSENNE_PRIMES[];
extern const uint32_t NUM_KNOWN_MERSENNE_PRIMES;

// Error codes
#define LLT_SUCCESS                 0
#define LLT_ERROR_INVALID_ARGS     -1
#define LLT_ERROR_MEMORY           -2
#define LLT_ERROR_FILE_IO          -3
#define LLT_ERROR_COMPUTATION      -4
#define LLT_ERROR_INVALID_EXPONENT -5

#ifdef __cplusplus
}
#endif

#endif // LUCAS_LEHMER_PREDICTOR_H