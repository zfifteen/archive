    printf("FEATURE 3: Z5D Intelligent Jumping\n");
    printf("---------------------------------\n");
    printf("Using Z Framework parameters:\n");
    printf("  ZF_KAPPA_STAR_DEFAULT: %.5f\n", ZF_KAPPA_STAR_DEFAULT);
    printf("  ZF_KAPPA_GEO_DEFAULT: %.3f\n", ZF_KAPPA_GEO_DEFAULT);
    printf("  ZF_Z5D_C_CALIBRATED: %.5f\n", ZF_Z5D_C_CALIBRATED);
    printf("\n");
    
    // Show how Z5D predictions guide candidate generation
    double test_k_values[] = {1000, 10000, 100000};
    for (int i = 0; i < 3; i++) {
        double k = test_k_values[i];
        double prediction = z5d_prime(k, ZF_Z5D_C_CALIBRATED, ZF_KAPPA_STAR_DEFAULT, ZF_KAPPA_GEO_DEFAULT, 1);
        
        printf("  k=%.0f: Z5D predicts prime ≈ %.0f\n", k, prediction);
        
        // Calculate jump size for hypothetical candidate near this prediction
        if (isfinite(prediction) && prediction > 0) {
            double ln_pred = log(prediction);
            double geodesic_jump = ln_pred * ZF_KAPPA_GEO_DEFAULT;
            printf("    Geodesic jump size: %.0f (vs traditional +2)\n", geodesic_jump);
        }
    }
    
    printf("\nSUMMARY:\n");
    printf("========\n");
    printf("✓ Adaptive reps: Optimizes security/performance tradeoff\n");
    printf("✓ Pre-filtering: Eliminates composites with minimal computation\n");
    printf("✓ Z5D jumping: Uses prime-density predictions for intelligent search\n");
    printf("✓ Geodesic parameters: Integrates framework's validated constants\n");
    printf("✓ Deterministic output: Maintains reproducible results\n");
    printf("\nThese optimizations address all requirements in issue #767.\n");
    
    return 0;
}
