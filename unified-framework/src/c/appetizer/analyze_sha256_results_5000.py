import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV data
df = pd.read_csv('bulk_analysis_results_5000.csv')

# Basic statistics
print("=== Basic Statistics for Coverage Percentages ===")
print(df['CoveragePercent'].describe())
print("\n=== Classification Distribution (Threshold 37.5%) ===")
print(df['Classification'].value_counts())
print("\n=== Coverage Distribution by Count ===")
print(df['AlignedCount'].value_counts().sort_index())

# Alignment Pattern Analysis: Count frequency of each bit position being set (1)
# Ensure AlignmentPattern is treated as string
def parse_pattern(pattern):
    try:
        pattern_str = str(pattern)
        if len(pattern_str) == 8:
            return [int(c) for c in pattern_str]
        else:
            return [0] * 8  # Fallback if pattern is invalid
    except:
        return [0] * 8

pattern_bits = df['AlignmentPattern'].apply(parse_pattern)
bit_freq = pd.DataFrame(pattern_bits.tolist(), columns=[f'H{i}' for i in range(8)]).mean() * 100
print("\n=== Percentage of Times Each Bit (H0-H7) is Set (Aligned) ===")
print(bit_freq)

# Pattern frequency: Top 10 most common alignment patterns
print("\n=== Top 10 Most Common Alignment Patterns ===")
print(df['AlignmentPattern'].value_counts().head(10))

# Input Length vs. Coverage Correlation
length_corr = df['InputLength'].corr(df['CoveragePercent'])
print("\n=== Correlation between Input Length and Coverage Percent ===")
print(f"Correlation Coefficient: {length_corr:.3f}")

# Group by input length ranges to see trends
bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, float('inf')]
labels = ['0-5', '6-10', '11-15', '16-20', '21-25', '26-30', '31-35', '36-40', '41-45', '46-50', '51-55', '56-60', '61-65', '66-70', '71-75', '76-80', '81-85', '86-90', '91-95', '96-100', '100+']
df['LengthRange'] = pd.cut(df['InputLength'], bins=bins, labels=labels, right=False)
length_group = df.groupby('LengthRange')['CoveragePercent'].mean()
length_group_count = df.groupby('LengthRange')['CoveragePercent'].count()
print("\n=== Average Coverage by Input Length Range ===")
print("Length Range | Average Coverage % | Count")
print("-------------|-------------------|------")
for idx in length_group.index:
    print(f"{idx} | {length_group[idx]:.1f} | {length_group_count[idx]}")

# Classification by length range
class_by_length = df.groupby('LengthRange')['Classification'].value_counts().unstack().fillna(0)
print("\n=== Classification Counts by Input Length Range ===")
print(class_by_length)

# State frequency: Top 10 most common states (64-bit hex values)
print("\n=== Top 10 Most Common States (Hex) ===")
print(df['StateHex'].value_counts().head(10))

# Visualize Coverage Distribution
plt.figure(figsize=(10, 6))
plt.hist(df['CoveragePercent'], bins=8, density=True, alpha=0.7, color='blue')
plt.title('Distribution of Coverage Percentages (Threshold 37.5%) - 5000 Inputs')
plt.xlabel('Coverage Percentage')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)
plt.savefig('coverage_distribution_5000.png')
plt.close()

# Visualize Bit Frequency
plt.figure(figsize=(8, 5))
bit_freq.plot(kind='bar', color='green')
plt.title('Percentage of Alignment per Bit Position (H0-H7) - 5000 Inputs')
plt.xlabel('Hash Word')
plt.ylabel('Alignment Frequency (%)')
plt.grid(True, axis='y', alpha=0.3)
plt.savefig('bit_frequency_5000.png')
plt.close()

# Visualize Coverage by Input Length
plt.figure(figsize=(10, 6))
colors = {'Aligned': 'green', 'Not Aligned': 'red'}
for cls in colors:
    subset = df[df['Classification'] == cls]
    plt.scatter(subset['InputLength'], subset['CoveragePercent'], c=colors[cls], label=cls, alpha=0.6)
plt.title('Coverage Percentage vs. Input Length - 5000 Inputs')
plt.xlabel('Input Length')
plt.ylabel('Coverage Percentage')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('coverage_vs_length_5000.png')
plt.close()

print("\n=== Visualizations Generated ===")
print("- coverage_distribution_5000.png: Histogram of coverage percentages")
print("- bit_frequency_5000.png: Bar chart of alignment frequency per bit position")
print("- coverage_vs_length_5000.png: Scatter plot of coverage vs. input length")

# Additional analysis: Check for consecutive state patterns (simple transition frequency)
states = df['StateHex'].tolist()
if len(states) > 1:
    transitions = [(states[i], states[i+1]) for i in range(len(states)-1)]
    transition_counts = pd.Series(transitions).value_counts().head(10)
    print("\n=== Top 10 Most Common State Transitions (Hex) ===")
    print(transition_counts)

# Entropy-like measure for input strings to check correlation with coverage
def calculate_entropy(s):
    try:
        s_str = str(s)
        if len(s_str) == 0:
            return 0
        length = len(s_str)
        freq = {}
        for char in s_str:
            freq[char] = freq.get(char, 0) + 1
        entropy = 0
        for count in freq.values():
            p = count / length
            entropy -= p * np.log2(p)
        return entropy
    except:
        return 0

df['Entropy'] = df['Input'].apply(calculate_entropy)
entropy_corr = df['Entropy'].corr(df['CoveragePercent'])
print("\n=== Correlation between Input Entropy and Coverage Percent ===")
print(f"Correlation Coefficient: {entropy_corr:.3f}")

# Group by entropy ranges
bins_entropy = [0, 1, 2, 3, 4, 5, 6, 7, 8, float('inf')]
labels_entropy = ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8+']
df['EntropyRange'] = pd.cut(df['Entropy'], bins=bins_entropy, labels=labels_entropy, right=False)
entropy_group = df.groupby('EntropyRange')['CoveragePercent'].mean()
entropy_group_count = df.groupby('EntropyRange')['CoveragePercent'].count()
print("\n=== Average Coverage by Input Entropy Range ===")
print("Entropy Range | Average Coverage % | Count")
print("--------------|-------------------|------")
for idx in entropy_group.index:
    print(f"{idx} | {entropy_group[idx]:.1f} | {entropy_group_count[idx]}")

# Additional pattern analysis: Check for bit-pair correlations (co-occurrence of 1s in pairs of positions)
bit_matrix = pd.DataFrame(pattern_bits.tolist(), columns=[f'H{i}' for i in range(8)])
bit_corr = bit_matrix.corr()
print("\n=== Correlation Matrix for Bit Positions (H0-H7 Alignment) ===")
print(bit_corr)

# Save bit correlation heatmap
plt.figure(figsize=(8, 6))
plt.imshow(bit_corr, cmap='coolwarm', interpolation='nearest', vmin=-1, vmax=1)
plt.colorbar(label='Correlation Coefficient')
plt.title('Correlation Heatmap of Alignment Across Bit Positions (H0-H7) - 5000 Inputs')
plt.xticks(range(8), [f'H{i}' for i in range(8)])
plt.yticks(range(8), [f'H{i}' for i in range(8)])
plt.savefig('bit_correlation_heatmap_5000.png')
plt.close()

print("\n=== Additional Visualization Generated ===")
print("- bit_correlation_heatmap_5000.png: Heatmap of bit position correlations")
