/**
 * Z Framework Parameters for Golden Spiral Implementation
 * =====================================================
 * 
 * Local parameter definitions for golden spiral Z5D candidate screening.
 * Maintains compatibility with the unified framework parameter system.
 * 
 * @file z_framework_params_golden.h
 * @author D.A.L. III (Dionisio Alberto Lopez III)
 * @version 1.0
 */

#ifndef Z_FRAMEWORK_PARAMS_GOLDEN_H
#define Z_FRAMEWORK_PARAMS_GOLDEN_H

// High-precision arithmetic configuration
#define ZF_MP_DPS 50                    // Decimal places (mpmath dps=50)
#define ZF_MPFR_PRECISION 166           // MPFR precision in bits (50 * 3.32)

// Z Framework calibration parameters
#define ZF_KAPPA_STAR 0.04449          // Z5D calibration parameter
#define ZF_KAPPA_GEO 0.3               // Geodesic mapping exponent

// Golden ratio constants (high precision)
#define ZF_PHI_STR "1.6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374847540880753868917521266338622235369317931800607667263544333890865959395829056383226613199282902678806752087668925017116962070322210432162695486262963136144"
#define ZF_PHI_INV_STR "0.6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374847540880753868917521266338622235369317931800607667263544333890865959395829056383226613199282902678806752087668925017116962070322210432162695486262963136144"

// Mathematical constants for golden space analysis
#define ZF_SQRT5_STR "2.2360679774997896964091736687312762354406183596115257242708972454105209256378048994374245057946134532147013059626406775321467925631892969121963440142137710986374906899994688669316507354160700024013993822542651128604863806048628649100055056026325829816982"
#define ZF_SQRT3_STR "1.7320508075688772935274463415058723669428052538103806280558069794519330169088000370811461867572485756756261414154067030299699450949989524788116555120943570808128915473289010963869020978999845649989906648550901008987152606969616965444843885853316094406350"

// Lucas-Lehmer specific constants for ℚ(√3) analysis
#define ZF_LL_ALPHA_BASE 2.0           // Base for Lucas sequence alpha = 2 + √3
#define ZF_LL_BETA_BASE 2.0            // Base for Lucas sequence beta = 2 - √3

// Statistical confidence parameters
#define ZF_BOOTSTRAP_SAMPLES 1000      // Bootstrap resamples for CI
#define ZF_CONFIDENCE_LEVEL 0.95       // 95% confidence interval

// Performance optimization thresholds
#define ZF_EARLY_EXIT_THRESHOLD 0.01   // Early termination threshold
#define ZF_MAX_ITERATIONS 1000000      // Maximum iterations for convergence

// Zeckendorf analysis parameters
#define ZF_ZECKENDORF_MAX_TERMS 50     // Maximum Fibonacci terms in representation
#define ZF_FIBONACCI_CACHE_SIZE 100    // Cache size for Fibonacci numbers

#endif // Z_FRAMEWORK_PARAMS_GOLDEN_H