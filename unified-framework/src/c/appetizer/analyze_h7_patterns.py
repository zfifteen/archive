import pandas as pd
import numpy as np

# Read the large dataset
df = pd.read_csv('bulk_analysis_results_5000.csv')

# Function to parse alignment pattern
def parse_pattern(pattern):
    try:
        pattern_str = str(pattern)
        if len(pattern_str) == 8:
            return [int(c) for c in pattern_str]
        return [0] * 8
    except:
        return [0] * 8

# Extract bit alignment for each position
pattern_bits = df['AlignmentPattern'].apply(parse_pattern)
bit_df = pd.DataFrame(pattern_bits.tolist(), columns=[f'H{i}' for i in range(8)])

# H7 alignment frequency
h7_freq = bit_df['H7'].mean() * 100
print(f"=== H7 Alignment Frequency ===")
print(f"H7 Aligned Percentage: {h7_freq:.1f}%")

# Compare with other bits
bit_freq = bit_df.mean() * 100
print("\n=== Alignment Frequency for All Bits (H0-H7) ===")
print(bit_freq)

# H7 alignment by coverage level (AlignedCount)
h7_by_coverage = df.groupby('AlignedCount')['AlignmentPattern'].apply(lambda x: pd.Series([str(p)[7] if len(str(p)) == 8 else '0' for p in x]).astype(int).mean() * 100)
print("\n=== H7 Alignment Percentage by Total Coverage Count ===")
print("Aligned Count | H7 Aligned %")
print("--------------|-------------")
for idx in h7_by_coverage.index:
    print(f"{idx:13d} | {h7_by_coverage[idx]:11.1f}")

# H7 alignment by input length range
bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, float('inf')]
labels = ['0-5', '6-10', '11-15', '16-20', '21-25', '26-30', '31-35', '36-40', '41-45', '46-50', '50+']
df['LengthRange'] = pd.cut(df['InputLength'], bins=bins, labels=labels, right=False)
h7_by_length = df.groupby('LengthRange').apply(lambda x: pd.Series([str(p)[7] if len(str(p)) == 8 else '0' for p in x['AlignmentPattern']]).astype(int).mean() * 100)
print("\n=== H7 Alignment Percentage by Input Length Range ===")
print("Length Range | H7 Aligned % | Count")
print("-------------|-------------|------")
length_group_count = df.groupby('LengthRange')['InputLength'].count()
for idx in h7_by_length.index:
    print(f"{idx:11} | {h7_by_length[idx]:11.1f} | {length_group_count[idx]}")

# Correlation of H7 with other bits
bit_corr = bit_df.corr()
h7_corr = bit_corr['H7']
print("\n=== Correlation of H7 Alignment with Other Bits (H0-H6) ===")
print(h7_corr[:-1])

# H7 alignment in specific input types (partial match for categories)
df['InputType'] = df['Input'].apply(lambda x: 'Numerical' if str(x).replace(';', '').isdigit() else 'Alphabetical' if str(x).replace(';', '').isalpha() else 'Mixed' if str(x).replace(';', '').isalnum() else 'Special' if any(c in str(x) for c in '!@#$%^&*()') else 'Other')
h7_by_type = df.groupby('InputType').apply(lambda x: pd.Series([str(p)[7] if len(str(p)) == 8 else '0' for p in x['AlignmentPattern']]).astype(int).mean() * 100)
h7_by_type_count = df.groupby('InputType')['Input'].count()
print("\n=== H7 Alignment Percentage by Input Type ===")
print("Input Type   | H7 Aligned % | Count")
print("-------------|-------------|------")
for idx in h7_by_type.index:
    print(f"{idx:12} | {h7_by_type[idx]:11.1f} | {h7_by_type_count[idx]}")
