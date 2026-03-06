#!/usr/bin/env python3
"""
Z5DHarness: Unified Harness for Toggleable Z5D Modes in Crypto/Bio

This module implements the exact Z5DHarness class as specified in issue #638,
providing a class-based harness for scalar/vectorized/hybrid modes with
logging metrics for both crypto and bio domains.

The harness enables ultra-batch scaling with cross-domain boosts, supporting:
- Crypto Domain: KS/χ² for bias detection, MI/AUC for entropy analysis
- Bio Domain: BioPython Seq alignments with Pearson correlation
- Processing Modes: scalar, vectorized, hybrid with configurable threshold
"""

import numpy as np
import mpmath as mp
from scipy.stats import pearsonr, ks_2samp, chi2_contingency
from sklearn.feature_selection import mutual_info_regression
from sklearn.metrics import roc_auc_score

# Import BioPython with proper namespace handling
try:
    import Bio.Seq
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False

mp.mp.dps = 50


class Z5DHarness:
    """
    Unified harness for toggleable Z5D modes in crypto/bio domains.
    
    Supports scalar/vectorized/hybrid processing modes for Z5D prime prediction
    with comprehensive statistical metrics logging for validation.
    """
    
    def __init__(self, mode='vectorized', threshold=1e6):
        """
        Initialize Z5DHarness with specified mode and threshold.
        
        Parameters
        ----------
        mode : str, optional
            Processing mode: 'scalar', 'vectorized', or 'hybrid' (default 'vectorized')
        threshold : float, optional
            Threshold for hybrid mode switching (default 1e6)
        """
        self.mode = mode
        self.threshold = threshold
    
    def z5d_prime(self, k_values):
        """
        Z5D prime prediction with mode-specific processing.

        Implements the exact algorithm specified in issue #638 with
        scalar/vectorized/hybrid mode switching based on configuration.

        Parameters
        ----------
        k_values : float or array_like
            Index values for Z5D prime prediction

        Returns
        -------
        float or ndarray
            Z5D prime predictions
        """
        # Handle mpmath objects and large numbers properly
        if hasattr(k_values, '__module__') and 'mpmath' in str(type(k_values)):
            # Single mpmath object - use high precision scalar path
            return self._z5d_prime_mpmath_scalar(k_values)

        # Try to convert to numpy array, but check for overflow
        try:
            k = np.array(k_values, dtype=np.float64)
            is_scalar_input = k.ndim == 0
            if is_scalar_input:
                k = k.reshape(1)

            # Check if any values are too large for float64
            if np.any(np.isinf(k)) or np.any(k > 1e308):
                # Fall back to mpmath scalar processing for large values
                if is_scalar_input:
                    return self._z5d_prime_mpmath_scalar(k_values)
                else:
                    return np.array([self._z5d_prime_mpmath_scalar(val) for val in k_values])
        except (OverflowError, ValueError):
            # Fall back to mpmath scalar processing
            if hasattr(k_values, '__iter__'):
                return np.array([self._z5d_prime_mpmath_scalar(val) for val in k_values])
            else:
                return self._z5d_prime_mpmath_scalar(k_values)
        
        mask = k >= 16
        results = np.array(k, dtype=object)

        if self.mode == 'scalar' or self.mode == 'hybrid':
            for i in np.where(mask)[0]:
                k_val = k[i]

                if self.mode == 'hybrid' and k_val < self.threshold:
                    # Numpy for low values
                    ln_k = np.log(k_val)
                    ln_ln_k = np.log(ln_k)
                    pnt = k_val * (ln_k + ln_ln_k - 1 + (ln_ln_k - 2) / ln_k)
                    ln_pnt = np.log(pnt)
                    d_k = (ln_pnt / np.exp(4))**2
                    e_k = (k_val**2 + k_val + 2) / (k_val * (k_val + 1) * (k_val + 2))
                    e_k *= 0.3 * (np.log(k_val + 1) / np.exp(2))
                    results[i] = pnt + (-0.00247) * d_k * pnt + 0.04449 * e_k * pnt
                else:
                    # mpmath for scalar/high precision
                    results[i] = self._z5d_prime_mpmath_scalar(k_val)
        else:  # vectorized
            k_masked = k[mask]
            if len(k_masked) > 0:
                # Check if any values are too large for vectorized processing
                if np.any(k_masked > 1e100):
                    return [self._z5d_prime_mpmath_scalar(k[i]) for i in np.where(mask)[0]]  # List of mpf
                else:
                    # Safe vectorized processing for smaller values
                    ln_k = np.log(k_masked)
                    ln_ln_k = np.log(ln_k)
                    pnt = k_masked * (ln_k + ln_ln_k - 1 + (ln_ln_k - 2) / ln_k)
                    ln_pnt = np.log(pnt)
                    d_k = (ln_pnt / np.exp(4))**2
                    e_k = (k_masked**2 + k_masked + 2) / (k_masked * (k_masked + 1) * (k_masked + 2))
                    e_k *= 0.3 * (np.log(k_masked + 1) / np.exp(2))
                    results[mask] = pnt + (-0.00247) * d_k * pnt + 0.04449 * e_k * pnt

        return results[0] if is_scalar_input else results

    def _z5d_prime_mpmath_scalar(self, k_val):
        """
        High-precision scalar Z5D prime prediction using mpmath.

        Parameters
        ----------
        k_val : mpmath.mpf or float
            Single k-value for prediction

        Returns
        -------
        mpmath.mpf
            Z5D prime prediction
        """
        if hasattr(k_val, '__module__') and 'mpmath' in str(type(k_val)):
            k_mp = k_val
        else:
            k_mp = mp.mpf(str(k_val))

        if k_mp < 16:
            return k_mp  # Return k for small values

        ln_k = mp.log(k_mp)
        ln_ln_k = mp.log(ln_k)
        pnt = k_mp * (ln_k + ln_ln_k - mp.mpf('1') + (ln_ln_k - mp.mpf('2')) / ln_k)
        ln_pnt = mp.log(pnt)

        # Lorentz-like adjustment for d_k to stabilize error for large k
        beta = mp.mpf('30.34')
        denom = mp.exp(mp.mpf('4')) + beta * ln_pnt
        d_k = (ln_pnt / denom)**2

        e_k = (k_mp**2 + k_mp + mp.mpf('2')) / (k_mp * (k_mp + mp.mpf('1')) * (k_mp + mp.mpf('2')))
        e_k *= mp.mpf('0.3') * (mp.log(k_mp + mp.mpf('1')) / mp.exp(mp.mpf('2')))

        # Adjusted coefficient for d_k term and return mpf to preserve precision
        result = pnt + mp.mpf('-54') * d_k * pnt + mp.mpf('0.04449') * e_k * pnt
        return result
    
    def crypto_metrics(self, batch_size=1000):
        """
        Calculate crypto domain metrics for bias detection.
        
        Parameters
        ----------
        batch_size : int, optional
            Number of predictions to process (default 1000)
            
        Returns
        -------
        dict
            Dictionary with KS, chi2, MI, and AUC metrics
        """
        k_values = np.arange(10000, 10000 + batch_size)
        embeds = self.z5d_prime(k_values)
        
        # Bias metrics (assume normal vs embeds)
        ks_stat = ks_2samp(embeds, np.random.normal(np.mean(embeds), np.std(embeds), batch_size))[0]
        
        # Chi-squared test
        try:
            hist_2d = np.histogram2d(embeds, np.roll(embeds, 1))[0]
            # Add small constant to avoid zeros
            hist_2d = hist_2d + 1e-10
            chi2 = chi2_contingency(hist_2d)[0]
        except (ValueError, Warning):
            chi2 = 0.0
        
        # Mutual information
        try:
            mi = mutual_info_regression(embeds.reshape(-1, 1), np.roll(embeds, 1))[0]
        except (ValueError, Warning):
            mi = 0.0
        
        # AUC score (proxy)
        try:
            labels = np.random.randint(0, 2, batch_size)
            norm_embeds = (embeds - embeds.min()) / (embeds.max() - embeds.min() + 1e-10)
            auc_score = roc_auc_score(labels, norm_embeds)
        except (ValueError, Warning):
            auc_score = 0.5
        
        return {
            'ks': ks_stat,
            'chi2': chi2,
            'mi': mi,
            'auc': auc_score
        }
    
    def bio_metrics(self, num_seqs=100):
        """
        Calculate bio domain metrics for genomic alignment analysis.
        
        Parameters
        ----------
        num_seqs : int, optional
            Number of sequences to analyze (default 100)
            
        Returns
        -------
        float
            Mean Pearson correlation coefficient
        """
        seqs = [''.join(np.random.choice(list('ACGT'), 100)) for _ in range(num_seqs)]
        seqs_mut = [s[1:] + s[0] for s in seqs]  # Simple mutation (circular shift)
        codes = [np.array([ord(c) for c in s]) for s in seqs]
        embeds = [self.z5d_prime(c) for c in codes]
        embeds_mut = [self.z5d_prime(np.array([ord(c) for c in s])) for s in seqs_mut]
        
        rs = []
        for e, em in zip(embeds, embeds_mut):
            try:
                r_val, _ = pearsonr(e.flatten(), em.flatten())
                rs.append(r_val if not np.isnan(r_val) else 0.0)
            except (ValueError, Warning):
                rs.append(0.0)
        
        return np.mean(rs)


# Example usage as shown in the problem statement
if __name__ == "__main__":
    # Example usage
    harness = Z5DHarness(mode='vectorized')
    crypto_met = harness.crypto_metrics()
    bio_r = harness.bio_metrics()
    print(crypto_met)
    print(bio_r)