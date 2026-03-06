/**
 * Prime Grid Plot - C Implementation using GMP
 * ============================================
 * 
 * C implementation of gists/prime_grid_plot.py using GMP for arbitrary precision integer arithmetic.
 * Plots points (x, y) where N = x * 10^m + y is prime, for a given base 10^m.
 * 
 * Key features:
 * - GMP-based arbitrary precision integer arithmetic for N = x*10^m + y calculations
 * - Miller-Rabin primality testing using GMP's mpz_probab_prime_p
 * - CSV output generation (no plotting - use external tools for visualization)
 * - Command-line interface matching Python version
 * 
 * Build: See Makefile in this directory
 * 
 * @file prime_grid_plot.c
 * @author Unified Framework Team (C Implementation)
 * @version 2.0
 */

#define _GNU_SOURCE  // For rand_r and getopt_long
#include <gmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <time.h>
#include <unistd.h>

// Configuration constants
#define MAX_FILENAME_LEN 1024
#define MAX_SCALE_STR_LEN 64
#define DEFAULT_MR_ROUNDS 25            // GMP default for mpz_probab_prime_p

// Program configuration structure
typedef struct {
    int m;                          // Exponent for 10^m
    long x_start, x_end;
    long y_start, y_end;
    long y_step;
    long probes;                    // Random probes (0 = disabled)
    int mr_rounds;
    unsigned int seed;              // Random seed (0 = use time)
    int use_seed;                   // Whether seed was specified
    char out_csv[MAX_FILENAME_LEN];
    int verbose;
} config_t;

// Statistics structure
typedef struct {
    long points_scanned;
    long primes_found;
    long composites_found;
} stats_t;

/**
 * Parse scale string like "10^6" or raw number "6"
 * Returns the exponent m, or -1 on error
 */
static int parse_scale(const char* scale_str) {
    if (!scale_str) return -1;
    
    // Check for "10^" prefix
    if (strncmp(scale_str, "10^", 3) == 0) {
        return atoi(scale_str + 3);
    }
    
    // Try parsing as raw integer
    int m = atoi(scale_str);
    if (m >= 0) return m;
    
    return -1;
}

/**
 * Miller-Rabin primality test using GMP
 * Returns 1 if n is probably prime, 0 if composite
 * Uses GMP's built-in mpz_probab_prime_p for proper primality testing
 */
static int gmp_primality_test(mpz_t n, int rounds) {
    // mpz_probab_prime_p returns:
    // 0 if n is definitely composite
    // 1 if n is probably prime (without being certain)  
    // 2 if n is definitely prime (for small numbers)
    int result = mpz_probab_prime_p(n, rounds);
    return (result >= 1) ? 1 : 0;
}

/**
 * Check if N = x * 10^m + y is probably prime using GMP
 */
static int is_grid_point_prime(long x, long y, int m, int mr_rounds) {
    
    mpz_t n, base, pow10m;
    mpz_init(n);
    mpz_init(base);
    mpz_init(pow10m);
    
    // Calculate 10^m using GMP's exact integer arithmetic
    mpz_ui_pow_ui(pow10m, 10, (unsigned long)m);
    
    // Calculate N = x * 10^m + y
    mpz_set_si(base, x);
    mpz_mul(base, base, pow10m);
    mpz_add_ui(n, base, (unsigned long)y);
    
    int result = gmp_primality_test(n, mr_rounds);
    
    mpz_clear(n); mpz_clear(base); mpz_clear(pow10m);
    return result;
}

/**
 * Generate random y values for probing
 */
static void generate_random_y_values(long y_start, long y_end, long num_probes, long* y_values, unsigned int* seed) {
    long range = y_end - y_start + 1;
    
    for (long i = 0; i < num_probes; i++) {
        long random_offset = rand_r(seed) % range;
        y_values[i] = y_start + random_offset;
    }
}

/**
 * Write CSV header
 */
static void write_csv_header(FILE* csv_file) {
    fprintf(csv_file, "x,y,N,is_prime\n");
}

/**
 * Write CSV row with the actual N value as a string using GMP
 */
static void write_csv_row(FILE* csv_file, long x, long y, int m, int is_prime) {
    mpz_t n, base, pow10m;
    mpz_init(n);
    mpz_init(base);
    mpz_init(pow10m);
    
    // Calculate N = x * 10^m + y using exact GMP arithmetic
    mpz_ui_pow_ui(pow10m, 10, (unsigned long)m);
    mpz_set_si(base, x);
    mpz_mul(base, base, pow10m);
    mpz_add_ui(n, base, (unsigned long)y);
    
    fprintf(csv_file, "%ld,%ld,", x, y);
    
    // Output the exact integer value using GMP's string conversion
    char* n_str = mpz_get_str(NULL, 10, n);
    fprintf(csv_file, "%s,%d\n", n_str, is_prime);
    free(n_str); // mpz_get_str allocates memory that must be freed
    
    mpz_clear(n); mpz_clear(base); mpz_clear(pow10m);
}

/**
 * Main grid processing function
 */
static void process_grid(const config_t* config, stats_t* stats) {
    FILE* csv_file = NULL;
    unsigned int seed = config->use_seed ? config->seed : (unsigned int)time(NULL);
    
    // Open CSV file if specified
    if (strlen(config->out_csv) > 0) {
        csv_file = fopen(config->out_csv, "w");
        if (!csv_file) {
            fprintf(stderr, "Error: Cannot open CSV file %s\n", config->out_csv);
            return;
        }
        write_csv_header(csv_file);
    }
    
    // Initialize statistics
    stats->points_scanned = 0;
    stats->primes_found = 0;
    stats->composites_found = 0;
    
    if (config->verbose) {
        printf("Processing grid with base 10^%d\n", config->m);
        printf("x range: [%ld, %ld]\n", config->x_start, config->x_end);
        printf("y range: [%ld, %ld]\n", config->y_start, config->y_end);
        if (config->probes > 0) {
            printf("Using %ld random probes per x value\n", config->probes);
        } else {
            printf("Using step size %ld for y iteration\n", config->y_step);
        }
        printf("Miller-Rabin rounds: %d\n", config->mr_rounds);
        printf("Random seed: %u\n", seed);
    }
    
    // Process each x value
    for (long x = config->x_start; x <= config->x_end; x++) {
        long* y_values = NULL;
        long num_y_values = 0;
        
        if (config->probes > 0) {
            // Random probing mode
            num_y_values = config->probes;
            y_values = malloc(num_y_values * sizeof(long));
            if (!y_values) {
                fprintf(stderr, "Error: Memory allocation failed\n");
                if (csv_file) fclose(csv_file);
                return;
            }
            generate_random_y_values(config->y_start, config->y_end, num_y_values, y_values, &seed);
        } else {
            // Stepped iteration mode
            num_y_values = (config->y_end - config->y_start) / config->y_step + 1;
            y_values = malloc(num_y_values * sizeof(long));
            if (!y_values) {
                fprintf(stderr, "Error: Memory allocation failed\n");
                if (csv_file) fclose(csv_file);
                return;
            }
            for (long i = 0; i < num_y_values; i++) {
                y_values[i] = config->y_start + i * config->y_step;
                if (y_values[i] > config->y_end) {
                    num_y_values = i;
                    break;
                }
            }
        }
        
        // Process each y value for this x
        for (long i = 0; i < num_y_values; i++) {
            long y = y_values[i];
            int is_prime = is_grid_point_prime(x, y, config->m, config->mr_rounds);
            
            stats->points_scanned++;
            if (is_prime) {
                stats->primes_found++;
            } else {
                stats->composites_found++;
            }
            
            // Write to CSV if enabled
            if (csv_file) {
                write_csv_row(csv_file, x, y, config->m, is_prime);
            }
            
            // Progress reporting for large jobs
            if (config->verbose && stats->points_scanned % 1000 == 0) {
                printf("Processed %ld points, found %ld primes\r", stats->points_scanned, stats->primes_found);
                fflush(stdout);
            }
        }
        
        free(y_values);
    }
    
    if (config->verbose && stats->points_scanned >= 1000) {
        printf("\n"); // New line after progress reporting
    }
    
    if (csv_file) {
        fclose(csv_file);
    }
}

/**
 * Print usage information
 */
static void print_usage(const char* program_name) {
    printf("Usage: %s [OPTIONS]\n", program_name);
    printf("\nPrime Grid Plot - C Implementation using GMP\n");
    printf("Plots points (x,y) where N = x*10^m + y is prime, at arbitrary scale.\n\n");
    printf("Required arguments:\n");
    printf("  --scale SCALE         Scale like '10^6' or raw exponent '6'\n");
    printf("  --x-start NUM         Start x (inclusive)\n");
    printf("  --x-end NUM           End x (inclusive)\n");
    printf("  --y-start NUM         Start y (inclusive)\n");
    printf("  --y-end NUM           End y (inclusive)\n");
    printf("\nOptional arguments:\n");
    printf("  --y-step NUM          Step for y traversal (default: 1, ignored if --probes > 0)\n");
    printf("  --probes NUM          Random probes in [y-start, y-end] (default: 0 = disabled)\n");
    printf("  --mr-rounds NUM       Miller-Rabin rounds for GMP primality test (default: %d)\n", DEFAULT_MR_ROUNDS);
    printf("  --seed NUM            Random seed for reproducible probes\n");
    printf("  --out-csv FILE        Output CSV file path (stores x,y,N,is_prime)\n");
    printf("  --verbose             Enable verbose output\n");
    printf("  --help                Show this help message\n");
    printf("\nExamples:\n");
    printf("  %s --scale \"10^6\" --x-start 1 --x-end 5 --y-start 0 --y-end 1000 --out-csv output.csv\n", program_name);
    printf("  %s --scale \"10^9\" --x-start 1 --x-end 3 --y-start 0 --y-end 1000000 --probes 1000\n", program_name);
}

/**
 * Parse command line arguments
 */
static int parse_arguments(int argc, char* argv[], config_t* config) {
    // Initialize config with defaults
    memset(config, 0, sizeof(config_t));
    config->m = -1;
    config->x_start = -1; config->x_end = -1;
    config->y_start = -1; config->y_end = -1;
    config->y_step = 1;
    config->probes = 0;
    config->mr_rounds = DEFAULT_MR_ROUNDS;
    config->use_seed = 0;
    config->verbose = 0;
    
    static struct option long_options[] = {
        {"scale",     required_argument, 0, 's'},
        {"x-start",   required_argument, 0, 'x'},
        {"x-end",     required_argument, 0, 'X'},
        {"y-start",   required_argument, 0, 'y'},
        {"y-end",     required_argument, 0, 'Y'},
        {"y-step",    required_argument, 0, 't'},
        {"probes",    required_argument, 0, 'p'},
        {"mr-rounds", required_argument, 0, 'r'},
        {"seed",      required_argument, 0, 'S'},
        {"out-csv",   required_argument, 0, 'c'},
        {"verbose",   no_argument,       0, 'v'},
        {"help",      no_argument,       0, 'h'},
        {0, 0, 0, 0}
    };
    
    int option_index = 0;
    int c;
    
    while ((c = getopt_long(argc, argv, "s:x:X:y:Y:t:p:r:S:c:vh", long_options, &option_index)) != -1) {
        switch (c) {
            case 's':
                config->m = parse_scale(optarg);
                if (config->m < 0) {
                    fprintf(stderr, "Error: Invalid scale '%s'\n", optarg);
                    return -1;
                }
                break;
            case 'x':
                config->x_start = atol(optarg);
                break;
            case 'X':
                config->x_end = atol(optarg);
                break;
            case 'y':
                config->y_start = atol(optarg);
                break;
            case 'Y':
                config->y_end = atol(optarg);
                break;
            case 't':
                config->y_step = atol(optarg);
                if (config->y_step <= 0) config->y_step = 1;
                break;
            case 'p':
                config->probes = atol(optarg);
                break;
            case 'r':
                config->mr_rounds = atoi(optarg);
                if (config->mr_rounds <= 0) config->mr_rounds = DEFAULT_MR_ROUNDS;
                break;
            case 'S':
                config->seed = (unsigned int)atol(optarg);
                config->use_seed = 1;
                break;
            case 'c':
                strncpy(config->out_csv, optarg, MAX_FILENAME_LEN - 1);
                config->out_csv[MAX_FILENAME_LEN - 1] = '\0';
                break;
            case 'v':
                config->verbose = 1;
                break;
            case 'h':
                print_usage(argv[0]);
                exit(0);
            case '?':
                return -1;
            default:
                return -1;
        }
    }
    
    // Validate required arguments
    if (config->m < 0) {
        fprintf(stderr, "Error: --scale is required\n");
        return -1;
    }
    if (config->x_start == -1 || config->x_end == -1) {
        fprintf(stderr, "Error: --x-start and --x-end are required\n");
        return -1;
    }
    if (config->y_start == -1 || config->y_end == -1) {
        fprintf(stderr, "Error: --y-start and --y-end are required\n");
        return -1;
    }
    
    // Validate ranges
    if (config->x_start > config->x_end) {
        fprintf(stderr, "Error: x-start must be <= x-end\n");
        return -1;
    }
    if (config->y_start > config->y_end) {
        fprintf(stderr, "Error: y-start must be <= y-end\n");
        return -1;
    }
    
    return 0;
}

/**
 * Main function
 */
int main(int argc, char* argv[]) {
    config_t config;
    stats_t stats;
    
    // Parse command line arguments
    if (parse_arguments(argc, argv, &config) != 0) {
        print_usage(argv[0]);
        return 1;
    }
    
    // Process the grid
    process_grid(&config, &stats);
    
    // Print final statistics
    printf("Done.\n");
    printf("points_scanned: %ld\n", stats.points_scanned);
    printf("primes_found: %ld\n", stats.primes_found);
    printf("composites_found: %ld\n", stats.composites_found);
    if (strlen(config.out_csv) > 0) {
        printf("out_csv: %s\n", config.out_csv);
    }
    printf("gmp_miller_rabin_rounds: %d\n", config.mr_rounds);
    
    return 0;
}