#!/bin/bash

# Script to summarize experiment results across different parameters and thresholds

# List of parameter combinations
k_values="0.02 0.03 0.04"
w_values="0.3 0.35 0.4"

# Print summary table header
echo "Summary of Alignment Rates and Coverage Across Parameter Combinations"
echo "===================================================================="
echo "k_star | width_factor | Mean Coverage % | Aligned % (25%) | Aligned % (37.5%) | Aligned % (50%) | Aligned % (62.5%)"
echo "-------|--------------|-----------------|-----------------|-------------------|-----------------|-------------------"

# Process each combination
for k in $k_values; do
    for w in $w_values; do
        file_name="results_k${k}_w${w}.csv"
        if [ -f "$file_name" ]; then
            # Count total rows (excluding header)
            total=$(wc -l < "$file_name")
            total=$((total - 1))
            if [ $total -gt 0 ]; then
                # Extract mean coverage using awk (average of CoveragePercent column)
                mean_coverage=$(awk -F, 'NR>1 {sum+=$3} END {if (NR>1) printf "%.1f", sum/(NR-1)}' "$file_name")
                # Count aligned for each threshold using AlignedCount column
                aligned_25=$(awk -F, 'NR>1 && $4 >= 2 {count++} END {printf "%.1f", (count*100)/NR}' "$file_name")
                aligned_375=$(awk -F, 'NR>1 && $4 >= 3 {count++} END {printf "%.1f", (count*100)/NR}' "$file_name")
                aligned_50=$(awk -F, 'NR>1 && $4 >= 4 {count++} END {printf "%.1f", (count*100)/NR}' "$file_name")
                aligned_625=$(awk -F, 'NR>1 && $4 >= 5 {count++} END {printf "%.1f", (count*100)/NR}' "$file_name")
                echo "$k     | $w           | $mean_coverage            | $aligned_25         | $aligned_375           | $aligned_50         | $aligned_625           "
            else
                echo "$k     | $w           | Empty file      | N/A             | N/A               | N/A             | N/A              "
            fi
        else
            echo "$k     | $w           | File not found  | N/A             | N/A               | N/A             | N/A              "
        fi
    done
done

# Detailed bit frequency and patterns for default parameters (k=0.03, w=0.35)
file_default="results_k0.03_w0.35.csv"
if [ -f "$file_default" ]; then
    echo "\n=== Bit Alignment Frequency for Default Parameters (k_star=0.03, width_factor=0.35) ==="
    # Calculate frequency of 1s in each bit position
    awk -F, 'NR>1 {for(i=1;i<=8;i++) bits[i]+=substr($5,i,1)} END {for(i=1;i<=8;i++) printf "H%d: %.1f%%\n", i-1, (bits[i]*100)/(NR-1)}' "$file_default"
    echo "\n=== Top 10 Alignment Patterns for Default Parameters ==="
    awk -F, 'NR>1 {patterns[$5]++} END {for(p in patterns) print p, patterns[p]}' "$file_default" | sort -k2 -nr | head -10
    echo "\n=== Coverage Distribution by Count for Default Parameters ==="
    awk -F, 'NR>1 {counts[$4]++} END {for(c in counts) print c " bits: " counts[c]}' "$file_default" | sort -n
fi
