import sqlite3
import pandas as pd
import numpy as np
import sympy as sp
import mpmath as mp
from scipy import stats
from scipy.stats import entropy
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import os
from math import log, e, pi, sin, floor
from functools import lru_cache

# Set mpmath precision for θ' computations
mp.mp.dps = 50

# Constants from Z model
PHI = (1 + mp.sqrt(5)) / 2  # Golden ratio
K_STAR = mp.mpf(0.313)  # Optimal curvature exponent
E_SQ = e ** 2  # ≈7.389, matching c column
BINS_THETA = 10  # For forbidden zone
BINS_HIST = 50  # For distributions
GMM_COMPONENTS = 5  # As per framework
FOURIER_M = 5  # Terms for asymmetry
BATCH_SIZE = 100000  # Memory-efficient chunk size for laptop
RESULTS_DIR = 'results/'
os.makedirs(RESULTS_DIR, exist_ok=True)

# Cache primality and divisor count
@lru_cache(maxsize=1000000)
def is_prime(n):
    return sp.isprime(n)

@lru_cache(maxsize=1000000)
def divisor_count(n):
    return len(sp.divisors(n))

# θ'(n, k) function
def theta_prime(n, k):
    mod_phi = mp.fmod(n, PHI)
    frac = mod_phi / PHI
    return PHI * mp.power(frac, k)

# Reconstruct κ(n) proxy using b or d(n) * ln(n+1)/c (c≈e²)
def kappa_proxy(n, b, c):
    d_n = divisor_count(n)
    return d_n * mp.log(n + 1) / c  # Use DB c for precision

# Chiral adjustment C(n) ≈ φ^{-1} * sin(ln n)
def chiral_adjust(n):
    return (1 / PHI) * mp.sin(mp.log(n))

# Disruption score proxy: Score = z * |Δf1| + ΔPeaks + ΔEntropy
# Simplified: Use Fourier diff for Δf1, bin peaks, entropy on O bins
def compute_disruption(df_batch, fourier_coeffs):
    # Proxy Δf1 as mean abs diff in Fourier coeffs
    delta_f1 = np.mean(np.abs(fourier_coeffs - np.mean(fourier_coeffs)))

    # ΔPeaks: Number of local maxima in O histogram
    o_hist, _ = np.histogram(df_batch['O'], bins=BINS_HIST)
    peaks = np.sum((o_hist[1:-1] > o_hist[:-2]) & (o_hist[1:-1] > o_hist[2:]))

    # ΔEntropy: Shannon on normalized O hist
    o_prob = o_hist / o_hist.sum()
    delta_entropy = entropy(o_prob)

    # Score weighted by mean z
    return df_batch['z'].mean() * delta_f1 + peaks + delta_entropy

# Fourier series fit for asymmetry S_b
def fourier_asymmetry(theta_norm):
    x = np.linspace(0, 1, len(theta_norm))
    y = np.sort(theta_norm)  # Density proxy via sorted
    coeffs = np.fft.rfft(y)[:FOURIER_M + 1]
    b_m = np.imag(coeffs[1:])  # Sine components
    return np.sum(np.abs(b_m))  # S_b

# Main analysis function
def run_analysis(db_path='z_embeddings.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Step 1: Data Preparation and Integrity Checks
    cursor.execute("SELECT COUNT(*) FROM z_embeddings")
    total_rows = cursor.fetchone()[0]
    print(f"Total rows: {total_rows}")

    cursor.execute("SELECT MIN(num), MAX(num) FROM z_embeddings")
    min_num, max_num = cursor.fetchone()
    print(f"Num range: {min_num} to {max_num}")

    # Check for nulls (per column example)
    null_counts = {}
    columns = ['num', 'b', 'c', 'z', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
    for col in columns[1:]:
        cursor.execute(f"SELECT COUNT(*) FROM z_embeddings WHERE {col} IS NULL")
        null_counts[col] = cursor.fetchone()[0]
    print(f"Null counts: {null_counts}")

    # Prime proportion estimate
    prime_count = 0
    composite_count = 0

    # Prepare summary stats DataFrames
    stats_primes = pd.DataFrame(index=columns[1:] + ['kappa', 'theta'], columns=['mean', 'std', 'min', 'max', 'skew', 'kurt'])
    stats_composites = stats_primes.copy()

    # For correlations, accumulators
    corr_matrix = np.zeros((len(columns)-1 + 2, len(columns)-1 + 2))  # Include kappa, theta
    extended_columns = columns[1:] + ['kappa', 'theta']
    count_batches = 0

    # For forbidden zone and enhancements
    theta_bins = np.linspace(0, 1, BINS_THETA + 1)
    count_n = np.zeros(BINS_THETA)
    count_p = np.zeros(BINS_THETA)

    # For GMM and PCA (fit on subsample)
    features = ['D', 'E', 'F', 'I', 'O']  # Key chain elements
    subsample_size = 100000  # For GMM/PCA to fit on laptop
    subsample = pd.DataFrame()

    # For var(O) vs log log num
    bin_edges = np.logspace(np.log10(max(1, min_num)), np.log10(max_num), 11)
    var_o_bins = np.zeros(len(bin_edges)-1)
    loglog_bins = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_counts = np.zeros(len(bin_edges)-1)

    # For disruption and Fourier
    disruption_scores = []
    s_b_values = []
    fourier_coeffs_list = []

    # Batch processing
    for start in range(min_num, max_num + 1, BATCH_SIZE):
        end = min(start + BATCH_SIZE - 1, max_num)
        query = f"SELECT * FROM z_embeddings WHERE num BETWEEN {start} AND {end}"
        df_batch = pd.read_sql_query(query, conn)

        if df_batch.empty:
            continue

        # Add prime flag, κ proxy, and θ' (early to propagate to subsets)
        df_batch['prime'] = df_batch['num'].apply(is_prime)
        df_batch['kappa'] = df_batch.apply(lambda row: float(kappa_proxy(row['num'], row['b'], row['c'])), axis=1)
        df_batch['theta'] = df_batch['num'].apply(lambda n: float(theta_prime(n, K_STAR)) / float(PHI))  # Normalize to [0,1)

        # Update counts
        prime_count += df_batch['prime'].sum()
        composite_count += len(df_batch) - df_batch['prime'].sum()

        # Grouped stats (accumulate)
        primes_batch = df_batch[df_batch['prime'] == True]
        composites_batch = df_batch[df_batch['prime'] == False]

        for col in extended_columns:
            if not primes_batch.empty:
                p_series = primes_batch[col]
                stats_primes.loc[col] += [p_series.mean(), p_series.std(), p_series.min(), p_series.max(),
                                          p_series.skew(), p_series.kurtosis()]
            if not composites_batch.empty:
                c_series = composites_batch[col]
                stats_composites.loc[col] += [c_series.mean(), c_series.std(), c_series.min(), c_series.max(),
                                              c_series.skew(), c_series.kurtosis()]

        count_batches += 1

        # Var(O) binning
        for i in range(len(bin_edges)-1):
            mask = (df_batch['num'] >= bin_edges[i]) & (df_batch['num'] < bin_edges[i+1])
            if mask.sum() > 1:  # Require >1 for var
                var_o_bins[i] = (var_o_bins[i] * bin_counts[i] + df_batch.loc[mask, 'O'].var() * mask.sum()) / (bin_counts[i] + mask.sum())
                bin_counts[i] += mask.sum()

        # Step 3: Hypothesis Testing (per batch, accumulate p-values or stats)
        ks_stats = {}
        t_stats = {}
        cohens_d = {}
        for col in extended_columns:
            if not primes_batch.empty and not composites_batch.empty and len(primes_batch[col].unique()) > 1 and len(composites_batch[col].unique()) > 1:
                ks_stat, ks_p = stats.ks_2samp(primes_batch[col], composites_batch[col])
                t_stat, t_p = stats.ttest_ind(primes_batch[col], composites_batch[col], equal_var=False)
                mean_diff = primes_batch[col].mean() - composites_batch[col].mean()
                pooled_std = np.sqrt((primes_batch[col].var() + composites_batch[col].var()) / 2)
                cohens_d[col] = mean_diff / pooled_std if pooled_std != 0 else 0
                ks_stats[col] = (ks_stat, ks_p)
                t_stats[col] = (t_stat, t_p)

        # KL divergence proxy (on O for example)
        if not primes_batch.empty and not composites_batch.empty:
            o_hist_p, _ = np.histogram(primes_batch['O'], bins=BINS_HIST, density=True)
            o_hist_c, _ = np.histogram(composites_batch['O'], bins=BINS_HIST, density=True)
            kl_div = entropy(o_hist_p + 1e-10, o_hist_c + 1e-10)  # Avoid zero

        # Forbidden zone
        theta_digit_p = np.digitize(primes_batch['theta'], theta_bins) - 1
        theta_digit_n = np.digitize(df_batch['theta'], theta_bins) - 1
        count_p += np.bincount(theta_digit_p, minlength=BINS_THETA)
        count_n += np.bincount(theta_digit_n, minlength=BINS_THETA)

        # Step 4: Correlations (Pearson on batch, average matrix)
        corr_batch = df_batch[extended_columns].corr(method='pearson').values
        corr_matrix += corr_batch
        # Sorted corr example: sort by num, r(delta vs kappa), delta proxy as {O}
        df_sorted = df_batch.sort_values('num')
        delta_proxy = df_sorted['O'] - np.floor(df_sorted['O'])
        r_delta_kappa, _ = stats.pearsonr(delta_proxy, df_sorted['kappa'])
        # Chiral boosted
        kappa_chiral = df_sorted['kappa'] + df_sorted['num'].apply(chiral_adjust)
        r_chiral, _ = stats.pearsonr(delta_proxy, kappa_chiral)

        # Regressions: O ~ log log num
        loglog_num = np.log(np.log(df_batch['num'] + 1e-10))
        model_o = sm.OLS(df_batch['O'], sm.add_constant(loglog_num)).fit()

        # Step 5: Clustering (accumulate subsample)
        if len(subsample) < subsample_size:
            to_add = min(len(df_batch), subsample_size - len(subsample))
            subsample = pd.concat([subsample, df_batch[features].sample(to_add)])

        # Fourier asymmetry on theta_norm
        theta_norm_batch = df_batch['theta']
        s_b_batch = fourier_asymmetry(theta_norm_batch)
        s_b_values.append(s_b_batch)

        # Fourier coeffs for disruption
        f_coeffs_batch = np.fft.rfft(np.sort(theta_norm_batch))[:FOURIER_M + 1]
        fourier_coeffs_list.append(f_coeffs_batch)

        # Step 6: Wave-CRISPR
        f_coeffs_mean = np.mean(fourier_coeffs_list, axis=0) if fourier_coeffs_list else np.zeros(FOURIER_M + 1)
        score_batch = compute_disruption(df_batch, f_coeffs_mean)
        disruption_scores.append(score_batch)

        # Prime gap proxy: for primes, ΔO
        if len(primes_batch) > 1:
            primes_sorted = primes_batch.sort_values('num')
            gaps = np.diff(primes_sorted['num'])
            delta_o = np.diff(primes_sorted['O'])
            r_gap_delta, _ = stats.pearsonr(gaps, np.abs(delta_o))

        print(f"Processed batch {start}-{end}")

    # Normalize accumulated stats
    if count_batches > 0:
        stats_primes /= count_batches
        stats_composites /= count_batches
        corr_matrix /= count_batches

    # Step 1 output
    prime_prop = prime_count / total_rows
    print(f"Prime proportion: {prime_prop:.4f}")
    stats_primes.to_csv(os.path.join(RESULTS_DIR, 'stats_primes.csv'))
    stats_composites.to_csv(os.path.join(RESULTS_DIR, 'stats_composites.csv'))

    # Var(O) plot
    plt.plot(loglog_bins, var_o_bins)
    plt.xlabel('log log num (bin centers)')
    plt.ylabel('var(O)')
    plt.savefig(os.path.join(RESULTS_DIR, 'var_o_vs_loglog.png'))

    # Step 3: Enhancements
    d_n = count_n / count_n.sum()
    d_p = count_p / count_p.sum()
    enhancements = np.where(d_n > 0, (d_p - d_n) / d_n * 100, -np.inf)
    max_e = np.max(enhancements)
    print(f"Max prime density enhancement: {max_e:.2f}%")
    # Forbidden zone [0.3,0.7) : bins 3-7 if [0,1) in 10 bins
    forb_zone = slice(3,7)
    prime_in_forb = count_p[forb_zone].sum() / count_p.sum() * 100 if count_p.sum() > 0 else 0
    print(f"Primes in forbidden zone [0.3,0.7): {prime_in_forb:.2f}%")

    # Correlation heatmap
    corr_df = pd.DataFrame(corr_matrix, index=extended_columns, columns=extended_columns)
    sns.heatmap(corr_df, annot=True, cmap='coolwarm')
    plt.savefig(os.path.join(RESULTS_DIR, 'corr_heatmap.png'))

    # Step 5: GMM on subsample
    if not subsample.empty:
        scaler = StandardScaler()
        sub_scaled = scaler.fit_transform(subsample)
        gmm = GaussianMixture(n_components=GMM_COMPONENTS)
        gmm.fit(sub_scaled)
        bic = gmm.bic(sub_scaled)
        aic = gmm.aic(sub_scaled)
        avg_sigma = np.mean(np.sqrt(gmm.covariances_.diagonal(axis1=1, axis2=2)))
        print(f"GMM BIC: {bic}, AIC: {aic}, avg sigma: {avg_sigma:.3f}")

        # PCA
        pca = PCA(n_components=2)
        sub_pca = pca.fit_transform(sub_scaled)
        plt.scatter(sub_pca[:,0], sub_pca[:,1])  # Color by prime if flagged in subsample
        plt.savefig(os.path.join(RESULTS_DIR, 'pca_2d.png'))

    # Average S_b
    avg_s_b = np.mean(s_b_values)
    print(f"Average Fourier asymmetry S_b: {avg_s_b:.3f}")

    # Average disruption
    avg_disruption = np.mean(disruption_scores)
    print(f"Average disruption score: {avg_disruption:.3f}")

    conn.close()

if __name__ == "__main__":
    run_analysis()