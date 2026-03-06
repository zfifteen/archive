import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV data
df = pd.read_csv('bulk_analysis_results.csv')

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
bins = [0, 5, 10, 15, 20, 25]
labels = ['0-5', '6-10', '11-15', '16-20', '21-25']
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
plt.title('Distribution of Coverage Percentages (Threshold 37.5%)')
plt.xlabel('Coverage Percentage')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)
plt.savefig('coverage_distribution.png')
plt.close()

# Visualize Bit Frequency
plt.figure(figsize=(8, 5))
bit_freq.plot(kind='bar', color='green')
plt.title('Percentage of Alignment per Bit Position (H0-H7)')
plt.xlabel('Hash Word')
plt.ylabel('Alignment Frequency (%)')
plt.grid(True, axis='y', alpha=0.3)
plt.savefig('bit_frequency.png')
plt.close()

# Visualize Coverage by Input Length
plt.figure(figsize=(10, 6))
colors = {'Aligned': 'green', 'Not Aligned': 'red'}
for cls in colors:
    subset = df[df['Classification'] == cls]
    plt.scatter(subset['InputLength'], subset['CoveragePercent'], c=colors[cls], label=cls, alpha=0.6)
plt.title('Coverage Percentage vs. Input Length')
plt.xlabel('Input Length')
plt.ylabel('Coverage Percentage')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('coverage_vs_length.png')
plt.close()

print("\n=== Visualizations Generated ===")
print("- coverage_distribution.png: Histogram of coverage percentages")
print("- bit_frequency.png: Bar chart of alignment frequency per bit position")
print("- coverage_vs_length.png: Scatter plot of coverage vs. input length")

# Additional analysis: Check for consecutive state patterns (simple transition frequency)
states = df['StateHex'].tolist()
if len(states) > 1:
    transitions = [(states[i], states[i+1]) for i in range(len(states)-1)]
    transition_counts = pd.Series(transitions).value_counts().head(5)
    print("\n=== Top 5 Most Common State Transitions (Hex) ===")
    print(transition_counts)

# Entropy-like measure for input strings to check correlation with coverage
def calculate_entropy(s):
    if len(s) == 0:
        return 0
    length = len(s)
    freq = {}
    for char in s:
        freq[char] = freq.get(char, 0) + 1
    entropy = 0
    for count in freq.values():
        p = count / length
        entropy -= p * np.log2(p)
    return entropy

df['Entropy'] = df['Input'].apply(calculate_entropy)
entropy_corr = df['Entropy'].corr(df['CoveragePercent'])
print("\n=== Correlation between Input Entropy and Coverage Percent ===")
print(f"Correlation Coefficient: {entropy_corr:.3f}")

# Group by entropy ranges
bins_entropy = [0, 1, 2, 3, 4, 5]
labels_entropy = ['0-1', '1-2', '2-3', '3-4', '4-5']
df['EntropyRange'] = pd.cut(df['Entropy'], bins=bins_entropy, labels=labels_entropy, right=False)
entropy_group = df.groupby('EntropyRange')['CoveragePercent'].mean()
entropy_group_count = df.groupby('EntropyRange')['CoveragePercent'].count()
print("\n=== Average Coverage by Input Entropy Range ===")
print("Entropy Range | Average Coverage % | Count")
print("--------------|-------------------|------")
for idx in entropy_group.index:
    print(f"{idx} | {entropy_group[idx]:.1f} | {entropy_group_count[idx]}")
