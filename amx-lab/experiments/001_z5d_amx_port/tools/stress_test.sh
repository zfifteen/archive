#!/bin/bash
# Fixed Stress Test - Runs CLI for 10 small n from CSV, 10 iterations
# Generates updated stress_report.md

# Ensure we are in the experiment root directory
if [[ -d "tools" && -d "bin" ]]; then
    :
else
    echo "Error: Must run from experiment root (experiments/001_z5d_amx_port/)"
    exit 1
fi

REPORT="stress_report.md"
rm -f "$REPORT"
echo "# Z5D Predictor Stress Test Report" > "$REPORT"
echo "Generated: $(date)" >> "$REPORT"
echo "Iterations: 10" >> "$REPORT"
echo "Test n: 100000 102000 104000 106000 108000 110000 112000 114000 116000 118000" >> "$REPORT"
echo "" >> "$REPORT"

expected_primes=("1299709" "1323803" "1347949" "1372123" "1396333" "1420531" "1444819" "1469101" "1493509" "1517897")

n_values=("100000" "102000" "104000" "106000" "108000" "110000" "112000" "114000" "116000" "118000")

times=()
matches=0
total_tests=0

get_time_ms() {
    python3 -c 'import time; print(int(time.time() * 1000))'
}

for iter in {1..10}; do
  echo "Iteration $iter/10"
  iter_times=()
  iter_matches=0
  for i in {0..9}; do
    n="${n_values[$i]}"
    expected="${expected_primes[$i]}"
    total_tests=$((total_tests + 1))
    
    start=$(get_time_ms)
    output=$("./bin/z5d_cli" "$n" 2>&1)
    end=$(get_time_ms)
    
    time_ms=$((end - start))
    iter_times+=("$time_ms")
    times+=("$time_ms")
    
    # Extract predicted prime. Output format: "Predicted prime for n=...: <prime>" or similar
    # Adjust grep/sed based on actual binary output
    predicted=$(echo "$output" | grep "Predicted prime" | awk -F': ' '{print $2}' | tr -d ' \r\n')
    
    if [[ "$predicted" == "$expected" ]]; then
      iter_matches=$((iter_matches + 1))
    fi
  done
  matches=$((matches + iter_matches))
  
  # Calculate average for this iteration
  sum=0
  for t in "${iter_times[@]}"; do sum=$((sum + t)); done
  avg_iter=$(echo "scale=2; $sum / ${#iter_times[@]}" | bc)
  
  echo "Iter $iter: Avg time $avg_iter ms, matches $iter_matches/10"
done

# Calculate overall average time
total_time_sum=0
for t in "${times[@]}"; do total_time_sum=$((total_time_sum + t)); done
avg_time=$(echo "scale=2; $total_time_sum / ${#times[@]}" | bc)

throughput=$(echo "scale=2; 1000 / $avg_time" | bc -l 2>/dev/null || echo "0")
accuracy_pct=$(echo "scale=2; $matches * 100 / $total_tests" | bc -l)

summary="Overall: Avg time $avg_time ms/pred, Throughput $throughput pred/s, Accuracy $matches/$total_tests ($accuracy_pct%)"
echo "$summary"
echo "$summary" >> "$REPORT"

echo "Report updated to $REPORT"
