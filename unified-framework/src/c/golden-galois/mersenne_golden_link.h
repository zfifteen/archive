#ifndef MERSENNE_GOLDEN_LINK_H
#define MERSENNE_GOLDEN_LINK_H

#include <mpfr.h>
#include <stdbool.h>
#include "golden_ratios.h"
#include "galois_field.h"

/**
 * @file mersenne_golden_link.h
 * @brief Analysis of connections between Mersenne primes and golden ratios
 * 
 * This module explores the theoretical connections between Mersenne primes
 * and golden ratio geometry, including invariance under Galois automorphisms
 * and cross-correlations between different golden ratio extensions.
 */

// Known Mersenne prime exponents (first 52 as of 2024)
extern const long KNOWN_MERSENNE_EXPONENTS[];
extern const int NUM_KNOWN_MERSENNE_EXPONENTS;

// Analysis result structure
typedef struct {
    long mersenne_exponent;           // Mersenne prime exponent p
    mpfr_t golden_phi_value;         // φ evaluated at specific context
    mpfr_t silver_ratio_value;       // Silver ratio evaluation
    mpfr_t tribonacci_value;         // Tribonacci evaluation
    bool galois_invariant;           // Invariant under φ ↔ φ̄
    mpfr_t trace_value;              // Trace in ℚ(√5)
    mpfr_t norm_value;               // Norm in ℚ(√5)
    mpfr_t cross_correlation;        // Cross-correlation measure
    bool geometric_point;            // Is it a geometric point in golden space?
    mpfr_prec_t precision;           // MPFR precision used
} mersenne_golden_analysis_t;

/**
 * Initialize Mersenne-Golden analysis structure
 * @param analysis Analysis structure to initialize
 * @param precision MPFR precision
 */
void mersenne_golden_init(mersenne_golden_analysis_t *analysis, mpfr_prec_t precision);

/**
 * Clear Mersenne-Golden analysis structure
 * @param analysis Analysis structure to clear
 */
void mersenne_golden_clear(mersenne_golden_analysis_t *analysis);

/**
 * Analyze specific Mersenne exponent for golden ratio connections
 * @param analysis Output analysis structure
 * @param mersenne_exp Mersenne prime exponent p
 * @param precision MPFR precision
 */
void mersenne_golden_analyze_exponent(mersenne_golden_analysis_t *analysis, 
                                     long mersenne_exp, mpfr_prec_t precision);

/**
 * Test if Mersenne exponent is invariant under Galois automorphism φ ↔ φ̄
 * This checks if the exponent exhibits special symmetry properties
 * @param mersenne_exp Mersenne prime exponent
 * @param tolerance Numerical tolerance
 * @param precision MPFR precision
 * @return true if invariant, false otherwise
 */
bool mersenne_golden_is_galois_invariant(long mersenne_exp, mpfr_t tolerance, 
                                        mpfr_prec_t precision);

/**
 * Compute golden ratio evaluated at Mersenne-specific context
 * Uses various methods: φ^p mod certain patterns, geometric interpretations
 * @param result Output MPFR variable
 * @param mersenne_exp Mersenne prime exponent
 * @param ratio_type Type of golden ratio
 * @param precision MPFR precision
 */
void mersenne_golden_evaluate_context(mpfr_t result, long mersenne_exp, 
                                     golden_ratio_type_t ratio_type, 
                                     mpfr_prec_t precision);

/**
 * Compute cross-correlation between different golden ratio extensions
 * Measures how silver ratio and tribonacci relate to standard φ for given Mersenne p
 * @param result Output correlation value
 * @param mersenne_exp Mersenne prime exponent
 * @param ratio1 First golden ratio type
 * @param ratio2 Second golden ratio type
 * @param precision MPFR precision
 */
void mersenne_golden_cross_correlation(mpfr_t result, long mersenne_exp,
                                      golden_ratio_type_t ratio1, 
                                      golden_ratio_type_t ratio2,
                                      mpfr_prec_t precision);

/**
 * Test if Mersenne exponent represents a geometric point in golden space
 * Based on theoretical criteria involving φ^2, trace/norm conditions
 * @param mersenne_exp Mersenne prime exponent
 * @param tolerance Numerical tolerance
 * @param precision MPFR precision
 * @return true if geometric point, false otherwise
 */
bool mersenne_golden_is_geometric_point(long mersenne_exp, mpfr_t tolerance, 
                                       mpfr_prec_t precision);

/**
 * Compute trace condition for Mersenne exponent in ℚ(√5)
 * Evaluates Tr(φ^p) and related expressions
 * @param result Output trace value
 * @param mersenne_exp Mersenne prime exponent
 * @param precision MPFR precision
 */
void mersenne_golden_trace_condition(mpfr_t result, long mersenne_exp, 
                                    mpfr_prec_t precision);

/**
 * Compute norm condition for Mersenne exponent in ℚ(√5)
 * Evaluates N(φ^p) and related expressions
 * @param result Output norm value
 * @param mersenne_exp Mersenne prime exponent
 * @param precision MPFR precision
 */
void mersenne_golden_norm_condition(mpfr_t result, long mersenne_exp, 
                                   mpfr_prec_t precision);

/**
 * Search for Mersenne primes invariant under specific golden ratio transformations
 * Systematic search through known and candidate Mersenne exponents
 * @param results Array to store found invariant exponents
 * @param max_results Maximum number of results to store
 * @param start_exp Starting Mersenne exponent for search
 * @param end_exp Ending Mersenne exponent for search
 * @param tolerance Numerical tolerance for invariance testing
 * @param precision MPFR precision
 * @return Number of invariant exponents found
 */
int mersenne_golden_search_invariant(long results[], int max_results,
                                    long start_exp, long end_exp,
                                    mpfr_t tolerance, mpfr_prec_t precision);

/**
 * Validate theoretical predictions against known Mersenne primes
 * Tests the golden-Galois theory against the 52 known Mersenne primes
 * @param tolerance Numerical tolerance
 * @param precision MPFR precision
 * @param verbose Enable verbose output
 * @return Number of successful validations
 */
int mersenne_golden_validate_theory(mpfr_t tolerance, mpfr_prec_t precision, bool verbose);

/**
 * Compute silver ratio (φ²) connections to Mersenne exponents
 * Explores φ² ≈ 2.414 relationships with Mersenne structure
 * @param result Output MPFR variable
 * @param mersenne_exp Mersenne prime exponent
 * @param precision MPFR precision
 */
void mersenne_golden_silver_analysis(mpfr_t result, long mersenne_exp, 
                                    mpfr_prec_t precision);

/**
 * Compute Tribonacci connections to Mersenne exponents
 * Explores cubic equation root relationships
 * @param result Output MPFR variable
 * @param mersenne_exp Mersenne prime exponent
 * @param precision MPFR precision
 */
void mersenne_golden_tribonacci_analysis(mpfr_t result, long mersenne_exp, 
                                        mpfr_prec_t precision);

/**
 * Generate comprehensive report for Mersenne-Golden analysis
 * @param analysis Analysis structure with computed results
 * @param verbose Enable verbose mathematical output
 */
void mersenne_golden_print_analysis(const mersenne_golden_analysis_t *analysis, bool verbose);

/**
 * Batch analysis of multiple Mersenne exponents
 * @param exponents Array of Mersenne exponents to analyze
 * @param num_exponents Number of exponents in array
 * @param precision MPFR precision
 * @param verbose Enable verbose output
 */
void mersenne_golden_batch_analysis(const long exponents[], int num_exponents,
                                   mpfr_prec_t precision, bool verbose);

/**
 * Export analysis results to CSV format
 * @param filename Output CSV filename
 * @param analyses Array of analysis results
 * @param num_analyses Number of analyses
 */
void mersenne_golden_export_csv(const char *filename, 
                               const mersenne_golden_analysis_t analyses[],
                               int num_analyses);

#endif // MERSENNE_GOLDEN_LINK_H