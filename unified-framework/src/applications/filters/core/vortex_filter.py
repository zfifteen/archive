import os
import sqlite3
import pandas as pd
import numpy as np

# Configuration
DB_FILE = "z_embeddings.db"
TABLE_NAME = "z_embeddings"
OUTPUT_DIR = "results"
CHUNKSIZE = 200_000        # rows per chunk; adjust to fit memory
SAMPLE_FRACTION = 0.01     # fraction of rows to sample for correlation
MAX_SAMPLE_ROWS = 200_000  # cap on total rows retained for correlation

os.makedirs(OUTPUT_DIR, exist_ok=True)

def update_stats(chunk, state, sample_frac=0.01):
    """
    Update running descriptive stats (count, mean, M2, min, max) and
    collect reservoir sample for quantiles.
    """
    num = chunk.select_dtypes(include=[np.number])
    n = len(num)
    if n == 0:
        return state

    count, mean, M2, col_min, col_max, samples = state

    chunk_mean = num.mean()
    chunk_var = num.var(ddof=0)

    if count == 0:
        count = n
        mean = chunk_mean
        M2 = chunk_var * n
        col_min = num.min()
        col_max = num.max()
    else:
        delta = chunk_mean - mean
        total = count + n
        mean += delta * (n / total)
        M2 += chunk_var * n + (delta**2) * (count * n / total)
        count = total
        col_min = np.minimum(col_min, num.min())
        col_max = np.maximum(col_max, num.max())

    samples.append(num.sample(frac=sample_frac, random_state=42))
    return (count, mean, M2, col_min, col_max, samples)

def finalize_stats(state):
    """
    From running state, compute final descriptive DataFrame.
    """
    count, mean, M2, col_min, col_max, samples = state
    std = np.sqrt(M2 / count) if count > 0 else np.nan

    if samples:
        sample_df = pd.concat(samples)
        quantiles = sample_df.quantile([0.25, 0.5, 0.75])
    else:
        quantiles = pd.DataFrame({0.25: mean, 0.5: mean, 0.75: mean})

    desc = pd.DataFrame({
        "count": count,
        "mean": mean,
        "std": std,
        "min": col_min,
        "25%": quantiles.loc[0.25],
        "50%": quantiles.loc[0.5],
        "75%": quantiles.loc[0.75],
        "max": col_max
    })

    return desc

def gather_correlation_samples(chunk, sample_frac, reservoir, max_rows):
    """
    Append a random subset of numeric rows to reservoir until max_rows.
    """
    if len(reservoir) >= max_rows:
        return reservoir

    num = chunk.select_dtypes(include=[np.number])
    sampled = num.sample(frac=sample_frac, random_state=42)
    reservoir.append(sampled)

    combined = pd.concat(reservoir)
    if len(combined) > max_rows:
        return [combined.sample(n=max_rows, random_state=42)]
    else:
        return reservoir

def main():
    # Connect to SQLite
    conn = sqlite3.connect(DB_FILE)

    # Initialize descriptive stats state
    desc_state = (0, None, None, None, None, [])

    # Initialize reservoir for correlation sampling
    corr_reservoir = []

    # Read table in chunks
    query = f"SELECT * FROM {TABLE_NAME}"
    for chunk in pd.read_sql_query(query, conn, chunksize=CHUNKSIZE):
        desc_state = update_stats(chunk, desc_state, sample_frac=SAMPLE_FRACTION)
        corr_reservoir = gather_correlation_samples(
            chunk,
            SAMPLE_FRACTION,
            corr_reservoir,
            MAX_SAMPLE_ROWS
        )

    conn.close()
    print(f"[PROCESSED] {TABLE_NAME} in {DB_FILE}")

    # Finalize and save descriptive statistics
    desc_df = finalize_stats(desc_state)
    desc_df.to_csv(f"{OUTPUT_DIR}/combined_descriptive_stats.csv", index=True)
    print(f"[SAVED] combined_descriptive_stats.csv")

    # Compute and save correlation matrix
    if corr_reservoir:
        corr_df = pd.concat(corr_reservoir)
        corr_matrix = corr_df.corr()
        corr_matrix.to_csv(f"{OUTPUT_DIR}/combined_correlation_matrix.csv", index=True)
        print(f"[SAVED] combined_correlation_matrix.csv")
    else:
        print("[WARNING] No rows sampled for correlation.")

if __name__ == "__main__":
    main()
