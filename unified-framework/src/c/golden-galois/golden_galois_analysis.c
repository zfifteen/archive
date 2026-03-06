#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <stdbool.h>
#include <mpfr.h>

#include "golden_ratios.h"
#include "galois_field.h"
#include "mersenne_golden_link.h"

/**
 * @file golden_galois_analysis.c
 * @brief Main executable for Multi-Base Golden Analysis and Galois Link
 * 
 * Command-line tool for exploring connections between golden ratio extensions
 * (φ, silver ratio, Tribonacci) and Mersenne primes via Galois field theory.
 */

// Command line options
static struct option long_options[] = {
    {"ratio",           required_argument, 0, 'r'},
    {"mersenne",        required_argument, 0, 'm'},
    {"mersenne-range",  required_argument, 0, 'R'},
    {"galois",          no_argument,       0, 'g'},
    {"cross-correlate", no_argument,       0, 'c'},
    {"precision",       required_argument, 0, 'p'},
    {"verbose",         no_argument,       0, 'v'},
    {"csv",             required_argument, 0, 'C'},
    {"validate",        no_argument,       0, 'V'},
    {"help",            no_argument,       0, 'h'},
    {0, 0, 0, 0}
};

typedef struct {
    golden_ratio_type_t ratio_type;
    bool all_ratios;
    long mersenne_exponent;
    long mersenne_start;
    long mersenne_end;
    bool analyze_galois;
    bool cross_correlate;
    unsigned int precision_bits;
    bool verbose;
    bool validate_theory;
    char *csv_output;
} program_options_t;

void print_help(const char *program_name) {
    printf("Multi-Base Golden Analysis and Galois Link\n");
    printf("==========================================\n\n");
    
    printf("Usage: %s [OPTIONS]\n\n", program_name);
    
    printf("Options:\n");
    printf("  -r, --ratio TYPE         Golden ratio type: phi, silver, tribonacci, all\n");
    printf("  -m, --mersenne P         Specific Mersenne exponent to analyze\n");
    printf("  -R, --mersenne-range P1,P2  Range of Mersenne exponents (P1 to P2)\n");
    printf("  -g, --galois             Enable Galois automorphism analysis\n");
    printf("  -c, --cross-correlate    Perform cross-correlation analysis\n");
    printf("  -p, --precision BITS     MPFR precision in bits (default: 256)\n");
    printf("  -v, --verbose            Enable verbose output\n");
    printf("  -C, --csv FILE           Export results to CSV file\n");
    printf("  -V, --validate           Validate theory against known Mersenne primes\n");
    printf("  -h, --help               Show this help message\n\n");
    
    printf("Examples:\n");
    printf("  %s --ratio phi --mersenne 31 --verbose\n", program_name);
    printf("  %s --ratio silver --galois --cross-correlate\n", program_name);
    printf("  %s --ratio all --mersenne-range 31,127 --precision 512\n", program_name);
    printf("  %s --validate --verbose\n", program_name);
    printf("  %s --ratio tribonacci --csv results.csv\n\n", program_name);
    
    printf("Mathematical Background:\n");
    printf("  φ (Golden ratio):  (1 + √5)/2 ≈ 1.618033988749\n");
    printf("  Silver ratio:      1 + √2 ≈ 2.414213562373\n");
    printf("  Tribonacci:        ψ ≈ 1.839286755214 (root of x³-x²-x-1=0)\n");
    printf("  Galois field:      ℚ(√5) with automorphisms φ ↔ φ̄\n\n");
    
    printf("Theory:\n");
    printf("  Explores Mersenne primes as geometric points in golden space,\n");
    printf("  investigating invariance under Galois automorphisms and\n");
    printf("  cross-correlations between different golden ratio extensions.\n\n");
}

golden_ratio_type_t parse_ratio_type(const char *ratio_str, bool *all_ratios) {
    *all_ratios = false;
    
    if (strcmp(ratio_str, "phi") == 0) {
        return GOLDEN_PHI;
    } else if (strcmp(ratio_str, "silver") == 0) {
        return GOLDEN_SILVER;
    } else if (strcmp(ratio_str, "tribonacci") == 0) {
        return GOLDEN_TRIBONACCI;
    } else if (strcmp(ratio_str, "all") == 0) {
        *all_ratios = true;
        return GOLDEN_PHI; // Default, will be overridden
    } else {
        printf("❌ Error: Unknown ratio type '%s'\n", ratio_str);
        printf("   Valid types: phi, silver, tribonacci, all\n");
        exit(EXIT_FAILURE);
    }
}

bool parse_mersenne_range(const char *range_str, long *start, long *end) {
    char *comma = strchr(range_str, ',');
    if (!comma) {
        return false;
    }
    
    *comma = '\0';
    *start = atol(range_str);
    *end = atol(comma + 1);
    *comma = ','; // Restore original string
    
    return (*start > 0 && *end > 0 && *start <= *end);
}

void analyze_single_ratio(golden_ratio_type_t ratio_type, const program_options_t *options) {
    mpfr_t ratio_value;
    mpfr_prec_t precision = options->precision_bits;
    
    mpfr_init2(ratio_value, precision);
    
    // Compute the golden ratio value
    switch (ratio_type) {
        case GOLDEN_PHI:
            golden_compute_phi(ratio_value, precision);
            break;
        case GOLDEN_SILVER:
            golden_compute_silver(ratio_value, precision);
            break;
        case GOLDEN_TRIBONACCI:
            golden_compute_tribonacci(ratio_value, precision, 100);
            break;
    }
    
    // Print ratio information
    golden_print_info(ratio_value, ratio_type, precision, options->verbose);
    
    // Galois analysis if requested
    if (options->analyze_galois && ratio_type == GOLDEN_PHI) {
        printf("🔄 Galois Automorphism Analysis:\n");
        
        galois_field_element_t phi_element, conjugate;
        galois_field_init(&phi_element, precision);
        galois_field_init(&conjugate, precision);
        
        galois_field_set_phi(&phi_element, precision);
        galois_field_apply_automorphism(&conjugate, &phi_element, GALOIS_AUTO_CONJUGATE);
        
        printf("   φ = ");
        galois_field_print(&phi_element, 15, false);
        printf("\n   φ̄ = ");
        galois_field_print(&conjugate, 15, false);
        printf("\n");
        
        mpfr_t trace, norm;
        mpfr_init2(trace, precision);
        mpfr_init2(norm, precision);
        
        galois_field_trace(trace, &phi_element);
        galois_field_norm(norm, &phi_element);
        
        printf("   Trace(φ) = ");
        mpfr_printf("%.Rf", trace);
        printf("\n   Norm(φ) = ");
        mpfr_printf("%.Rf", norm);
        printf("\n\n");
        
        galois_field_clear(&phi_element);
        galois_field_clear(&conjugate);
        mpfr_clear(trace);
        mpfr_clear(norm);
    }
    
    mpfr_clear(ratio_value);
}

void analyze_mersenne_connection(const program_options_t *options) {
    if (options->mersenne_exponent > 0) {
        // Single Mersenne exponent analysis
        mersenne_golden_analysis_t analysis;
        mersenne_golden_init(&analysis, options->precision_bits);
        
        mersenne_golden_analyze_exponent(&analysis, options->mersenne_exponent, 
                                       options->precision_bits);
        mersenne_golden_print_analysis(&analysis, options->verbose);
        
        if (options->csv_output) {
            mersenne_golden_export_csv(options->csv_output, &analysis, 1);
        }
        
        mersenne_golden_clear(&analysis);
        
    } else if (options->mersenne_start > 0 && options->mersenne_end > 0) {
        // Range analysis
        printf("🔢 Analyzing Mersenne exponent range %ld to %ld\n\n", 
               options->mersenne_start, options->mersenne_end);
        
        long range_size = options->mersenne_end - options->mersenne_start + 1;
        if (range_size > 100) {
            printf("⚠️  Warning: Large range (%ld exponents). This may take time.\n\n", range_size);
        }
        
        mersenne_golden_analysis_t *analyses = malloc(range_size * sizeof(mersenne_golden_analysis_t));
        if (!analyses) {
            printf("❌ Error: Cannot allocate memory for range analysis\n");
            return;
        }
        
        int analysis_count = 0;
        for (long p = options->mersenne_start; p <= options->mersenne_end; p++) {
            mersenne_golden_init(&analyses[analysis_count], options->precision_bits);
            mersenne_golden_analyze_exponent(&analyses[analysis_count], p, 
                                           options->precision_bits);
            
            if (!options->verbose) {
                printf("p=%ld: Galois=%s, Geometric=%s\n", p,
                       analyses[analysis_count].galois_invariant ? "Y" : "N",
                       analyses[analysis_count].geometric_point ? "Y" : "N");
            }
            
            analysis_count++;
        }
        
        if (options->csv_output) {
            mersenne_golden_export_csv(options->csv_output, analyses, analysis_count);
        }
        
        // Cleanup
        for (int i = 0; i < analysis_count; i++) {
            mersenne_golden_clear(&analyses[i]);
        }
        free(analyses);
    }
}

void perform_cross_correlation(const program_options_t *options) {
    printf("🔗 Cross-Correlation Analysis\n");
    printf("=============================\n\n");
    
    mpfr_t correlation_phi_silver, correlation_phi_tribonacci, correlation_silver_tribonacci;
    mpfr_prec_t precision = options->precision_bits;
    
    mpfr_init2(correlation_phi_silver, precision);
    mpfr_init2(correlation_phi_tribonacci, precision);
    mpfr_init2(correlation_silver_tribonacci, precision);
    
    long test_exponent = (options->mersenne_exponent > 0) ? options->mersenne_exponent : 31;
    
    mersenne_golden_cross_correlation(correlation_phi_silver, test_exponent,
                                    GOLDEN_PHI, GOLDEN_SILVER, precision);
    mersenne_golden_cross_correlation(correlation_phi_tribonacci, test_exponent,
                                    GOLDEN_PHI, GOLDEN_TRIBONACCI, precision);
    mersenne_golden_cross_correlation(correlation_silver_tribonacci, test_exponent,
                                    GOLDEN_SILVER, GOLDEN_TRIBONACCI, precision);
    
    printf("Cross-correlations for Mersenne exponent %ld:\n\n", test_exponent);
    printf("   φ ↔ Silver ratio:      ");
    mpfr_printf("%.Rf", correlation_phi_silver);
    printf("\n   φ ↔ Tribonacci:        ");
    mpfr_printf("%.Rf", correlation_phi_tribonacci);
    printf("\n   Silver ↔ Tribonacci:   ");
    mpfr_printf("%.Rf", correlation_silver_tribonacci);
    printf("\n\n");
    
    mpfr_clear(correlation_phi_silver);
    mpfr_clear(correlation_phi_tribonacci);
    mpfr_clear(correlation_silver_tribonacci);
}

int main(int argc, char *argv[]) {
    program_options_t options = {
        .ratio_type = GOLDEN_PHI,
        .all_ratios = false,
        .mersenne_exponent = 0,
        .mersenne_start = 0,
        .mersenne_end = 0,
        .analyze_galois = false,
        .cross_correlate = false,
        .precision_bits = 256,
        .verbose = false,
        .validate_theory = false,
        .csv_output = NULL
    };
    
    int c;
    while ((c = getopt_long(argc, argv, "r:m:R:gcp:vC:Vh", long_options, NULL)) != -1) {
        switch (c) {
            case 'r':
                options.ratio_type = parse_ratio_type(optarg, &options.all_ratios);
                break;
            case 'm':
                options.mersenne_exponent = atol(optarg);
                if (options.mersenne_exponent <= 0) {
                    printf("❌ Error: Invalid Mersenne exponent %s\n", optarg);
                    return EXIT_FAILURE;
                }
                break;
            case 'R':
                if (!parse_mersenne_range(optarg, &options.mersenne_start, &options.mersenne_end)) {
                    printf("❌ Error: Invalid range format '%s'. Use 'start,end'\n", optarg);
                    return EXIT_FAILURE;
                }
                break;
            case 'g':
                options.analyze_galois = true;
                break;
            case 'c':
                options.cross_correlate = true;
                break;
            case 'p':
                options.precision_bits = atoi(optarg);
                if (options.precision_bits < 64 || options.precision_bits > 4096) {
                    printf("❌ Error: Precision must be between 64 and 4096 bits\n");
                    return EXIT_FAILURE;
                }
                break;
            case 'v':
                options.verbose = true;
                break;
            case 'C':
                options.csv_output = optarg;
                break;
            case 'V':
                options.validate_theory = true;
                break;
            case 'h':
                print_help(argv[0]);
                return EXIT_SUCCESS;
            case '?':
                printf("❌ Error: Unknown option. Use --help for usage information.\n");
                return EXIT_FAILURE;
        }
    }
    
    // Initialize MPFR precision
    golden_init_precision(options.precision_bits);
    
    printf("🌟 Multi-Base Golden Analysis and Galois Link\n");
    printf("=============================================\n\n");
    
    if (options.verbose) {
        printf("🔧 Configuration:\n");
        printf("   MPFR precision: %u bits\n", options.precision_bits);
        printf("   Ratio analysis: %s\n", options.all_ratios ? "All ratios" : "Single ratio");
        printf("   Galois analysis: %s\n", options.analyze_galois ? "Enabled" : "Disabled");
        printf("   Cross-correlation: %s\n", options.cross_correlate ? "Enabled" : "Disabled");
        printf("\n");
    }
    
    // Theory validation
    if (options.validate_theory) {
        mpfr_t tolerance;
        mpfr_init2(tolerance, options.precision_bits);
        mpfr_set_str(tolerance, "1e-50", 10, MPFR_RNDN);
        
        int validated = mersenne_golden_validate_theory(tolerance, options.precision_bits, 
                                                       options.verbose);
        
        printf("🏆 Theory validation: %d/52 known Mersenne primes analyzed\n\n", validated);
        
        mpfr_clear(tolerance);
    }
    
    // Golden ratio analysis
    if (options.all_ratios) {
        analyze_single_ratio(GOLDEN_PHI, &options);
        analyze_single_ratio(GOLDEN_SILVER, &options);
        analyze_single_ratio(GOLDEN_TRIBONACCI, &options);
    } else {
        analyze_single_ratio(options.ratio_type, &options);
    }
    
    // Mersenne connection analysis
    if (options.mersenne_exponent > 0 || (options.mersenne_start > 0 && options.mersenne_end > 0)) {
        analyze_mersenne_connection(&options);
    }
    
    // Cross-correlation analysis
    if (options.cross_correlate) {
        perform_cross_correlation(&options);
    }
    
    // Default demo if no specific analysis requested
    if (!options.validate_theory && options.mersenne_exponent == 0 && 
        options.mersenne_start == 0 && !options.cross_correlate) {
        
        printf("📚 Quick demonstration (use --help for more options):\n\n");
        
        // Show golden ratio values
        mpfr_t phi, silver, tribonacci;
        mpfr_init2(phi, options.precision_bits);
        mpfr_init2(silver, options.precision_bits);
        mpfr_init2(tribonacci, options.precision_bits);
        
        golden_compute_phi(phi, options.precision_bits);
        golden_compute_silver(silver, options.precision_bits);
        golden_compute_tribonacci(tribonacci, options.precision_bits, 100);
        
        printf("Golden ratio values:\n");
        printf("   φ = ");
        mpfr_printf("%.Rf", phi);
        printf("\n   Silver = ");
        mpfr_printf("%.Rf", silver);
        printf("\n   Tribonacci = ");
        mpfr_printf("%.Rf", tribonacci);
        printf("\n\n");
        
        // Quick Mersenne analysis
        printf("Quick Mersenne analysis (M₅, p=31):\n");
        mersenne_golden_analysis_t demo_analysis;
        mersenne_golden_init(&demo_analysis, options.precision_bits);
        mersenne_golden_analyze_exponent(&demo_analysis, 31, options.precision_bits);
        
        printf("   Galois invariant: %s\n", demo_analysis.galois_invariant ? "Yes" : "No");
        printf("   Geometric point: %s\n", demo_analysis.geometric_point ? "Yes" : "No");
        printf("   Cross-correlation: ");
        mpfr_printf("%.Rf", demo_analysis.cross_correlation);
        printf("\n\n");
        
        printf("💡 Try: %s --validate --verbose\n", argv[0]);
        printf("💡 Try: %s --ratio phi --mersenne 127 --galois --verbose\n", argv[0]);
        
        mpfr_clear(phi);
        mpfr_clear(silver);
        mpfr_clear(tribonacci);
        mersenne_golden_clear(&demo_analysis);
    }
    
    return EXIT_SUCCESS;
}