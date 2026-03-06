#!/bin/bash
# Quick Start Script for θ′-Biased Ordering Experiment
# Runs a quick test to verify the experiment works

set -e  # Exit on error

echo "========================================================================"
echo "θ′-Biased Ordering via Golden LCG Experiment - Quick Start"
echo "========================================================================"
echo

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✓ Python: $python_version"
echo

# Run individual component tests
echo "Step 1: Testing Golden LCG..."
python3 golden_lcg.py
echo

echo "Step 2: Testing θ′-biased ordering..."
python3 theta_prime_bias.py
echo

echo "Step 3: Testing RSA QMC..."
python3 rsa_qmc_test.py
echo

echo "Step 4: Testing CRISPR spectral..."
python3 crispr_spectral_test.py
echo

echo "Step 5: Testing crypto rekey..."
python3 crypto_rekey_test.py
echo

echo "Step 6: Testing cross-validation..."
python3 cross_validation.py
echo

# Run full experiment (quick mode)
echo "========================================================================"
echo "Step 7: Running full experiment (quick mode)..."
echo "========================================================================"
echo
python3 run_experiment.py --quick
echo

# Generate summary
echo "========================================================================"
echo "Step 8: Generating summary report..."
echo "========================================================================"
echo
python3 generate_summary.py
echo

# Check for matplotlib
if python3 -c "import matplotlib" 2>/dev/null; then
    echo "========================================================================"
    echo "Step 9: Generating plots..."
    echo "========================================================================"
    echo
    python3 generate_plots.py
    echo
    echo "✓ Plots generated in plots/ directory"
else
    echo "Note: matplotlib not available, skipping plot generation"
    echo "      (Install with: pip install matplotlib)"
fi

echo
echo "========================================================================"
echo "EXPERIMENT COMPLETE!"
echo "========================================================================"
echo
echo "Results available in:"
echo "  - results/experiment_results.json  (JSON format)"
echo "  - results/experiment_summary.txt   (text format)"
if python3 -c "import matplotlib" 2>/dev/null; then
    echo "  - plots/*.png                      (visualizations)"
fi
echo
echo "To run the full experiment with n=1000 bootstrap:"
echo "  python3 run_experiment.py"
echo
