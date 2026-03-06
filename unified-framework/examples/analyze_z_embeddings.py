"""
python analyze_z_embeddings.py \
  --input z_embeddings_10.csv \
  --output-dir results/ \
  --sample-fraction 0.1

"""
import os
import argparse
import pandas as pd
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute descriptive stats and correlation matrix for a large CSV."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to input CSV (e.g., z_embeddings_10.csv)"
    )
    parser.add_argument(
        "--output-dir", "-o", default=".",
        help="Directory to save results"
    )
    parser.add_argument(
        "--sample-fraction", "-s", type=float, default=1.0,
        help="Fraction of rows to sample for correlation (0 < s <= 1.0)"
    )
    parser.add_argument(
        "--chunksize", "-c", type=int, default=None,
        help="If set, read CSV in chunks of this many rows to reduce memory usage"
    )
    return parser.parse_args()

def compute_descriptive_stats(df_iter, chunksize=None):
    """
    Compute mean, std, min, 25%, 50%, 75%, max across the dataset.
    If chunksize is provided, df_iter yields chunks; else, df_iter is a single DataFrame.
    """
    # Initialize accumulators for online mean & M2 (variance)
    count = 0
    means = None
    M2 = None
    mins = None
    maxs = None
    # Collect percentiles from a random subset if chunking
    sample_vals = []

    for chunk in df_iter:
        numeric = chunk.select_dtypes(include=[np.number])
        # Update count, mean, M2
        n = len(numeric)
        if n == 0:
            continue
        chunk_mean = numeric.mean()
        chunk_var = numeric.var(ddof=0)
        if means is None:
            means = chunk_mean
            M2 = chunk_var * n
            count = n
            mins = numeric.min()
            maxs = numeric.max()
        else:
            # Welford update
            delta = chunk_mean - means
            total_count = count + n
            means += delta * (n / total_count)
            M2 += chunk_var * n + delta**2 * (count * n / total_count)
            count = total_count
            mins = np.minimum(mins, numeric.min())
            maxs = np.maximum(maxs, numeric.max())
        # store small random sample for percentiles
        sample_vals.append(numeric.sample(
            frac=min(0.01, 1.0), random_state=42
        if len(numeric) > 0:
            sample_vals.append(numeric.sample(
                frac=min(0.01, 1.0), random_state=42
            ))

    # finalize stats
    stds = np.sqrt(M2 / count)
    sample_df = pd.concat(sample_vals)
    quantiles = sample_df.quantile([0.25, 0.5, 0.75])

    desc = pd.DataFrame({
        "count": count,
        "mean": means,
        "std": stds,
        "min": mins,
        "25%": quantiles.loc[0.25],
        "50%": quantiles.loc[0.5],
        "75%": quantiles.loc[0.75],
        "max": maxs
    })

    return desc

def compute_correlation(df, sample_fraction):
    """
    Compute Pearson correlation matrix on a random sample of rows to save memory.
    """
    if sample_fraction < 1.0:
        df = df.sample(frac=sample_fraction, random_state=42)
    numeric = df.select_dtypes(include=[np.number])
    return numeric.corr()

def main():
    args = parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    input_path = args.input

    if args.chunksize:
        reader = pd.read_csv(input_path, chunksize=args.chunksize)
    else:
        reader = [pd.read_csv(input_path)]

    # Descriptive statistics
    print("Computing descriptive statistics...")
    desc = compute_descriptive_stats(reader, chunksize=args.chunksize)
    desc_path = os.path.join(args.output_dir, "descriptive_stats.csv")
    desc.to_csv(desc_path)
    print(f"- Saved descriptive stats to {desc_path}")

    # Reload full DataFrame for correlation (to avoid exhaustion of iterator)
    print("Loading full DataFrame for correlation analysis...")
    df_full = pd.read_csv(input_path)
    corr = compute_correlation(df_full, args.sample_fraction)
    corr_path = os.path.join(args.output_dir, "correlation_matrix.csv")
    corr.to_csv(corr_path)
    print(f"- Saved correlation matrix to {corr_path}")

if __name__ == "__main__":
    main()
