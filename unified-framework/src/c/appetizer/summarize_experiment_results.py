import pandas as pd
import os

# List of parameter combinations
k_values = ['0.02', '0.03', '0.04']
w_values = ['0.3', '0.35', '0.4']

# Thresholds to analyze
thresholds = {
    '25': 2,  # >=2/8 bits
    '37.5': 3,  # >=3/8 bits
    '50': 4,   # >=4/8 bits
    '62.5': 5   # >=5/8 bits
}

# Summary table header
print("Summary of Alignment Rates and Coverage Across Parameter Combinations")
print("====================================================================")
print("k_star | width_factor | Mean Coverage % | Aligned % (25%) | Aligned % (37.5%) | Aligned % (50%) | Aligned % (62.5%)")
print("-------|--------------|-----------------|-----------------|-------------------|-----------------|-------------------")

# Process each combination
for k in k_values:
    for w in w_values:
        file_name = f"results_k{k}_w{w}.csv"
        if os.path.exists(file_name):
            try:
                # Attempt to read with utf-8, fallback to latin1 if fails, or skip bad lines
                try:
                    df = pd.read_csv(file_name, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_name, encoding='latin1', errors='ignore')
                mean_coverage = df['CoveragePercent'].mean()
                aligned_25 = (df['AlignedCount'] >= thresholds['25']).mean() * 100
                aligned_375 = (df['AlignedCount'] >= thresholds['37.5']).mean() * 100
                aligned_50 = (df['AlignedCount'] >= thresholds['50']).mean() * 100
                aligned_625 = (df['AlignedCount'] >= thresholds['62.5']).mean() * 100
                print(f"{k:6} | {w:12} | {mean_coverage:15.1f} | {aligned_25:15.1f} | {aligned_375:17.1f} | {aligned_50:15.1f} | {aligned_625:17.1f}")
            except Exception as e:
                print(f"{k:6} | {w:12} | Error: {str(e)[:30]} | N/A             | N/A               | N/A             | N/A              ")
        else:
            print(f"{k:6} | {w:12} | File not found | N/A             | N/A               | N/A             | N/A              ")

# Detailed bit frequency for default parameters (k=0.03, w=0.35)
def parse_pattern(pattern):
    try:
        pattern_str = str(pattern)
        if len(pattern_str) == 8:
            return [int(c) for c in pattern_str]
        return [0] * 8
    except:
        return [0] * 8

file_default = "results_k0.03_w0.35.csv"
if os.path.exists(file_default):
    try:
        df_default = pd.read_csv(file_default, encoding='utf-8')
    except UnicodeDecodeError:
        df_default = pd.read_csv(file_default, encoding='latin1', errors='ignore')
    pattern_bits = df_default['AlignmentPattern'].apply(parse_pattern)
    bit_freq = pd.DataFrame(pattern_bits.tolist(), columns=[f'H{i}' for i in range(8)]).mean() * 100
    print("\n=== Bit Alignment Frequency for Default Parameters (k_star=0.03, width_factor=0.35) ===")
    print(bit_freq)
    print("\n=== Top 10 Alignment Patterns for Default Parameters ===")
    print(df_default['AlignmentPattern'].value_counts().head(10))
    print("\n=== Coverage Distribution by Count for Default Parameters ===")
    print(df_default['AlignedCount'].value_counts().sort_index())
