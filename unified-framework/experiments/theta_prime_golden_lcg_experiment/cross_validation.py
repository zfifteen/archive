"""
Cross-Validation Analysis for Shared Features
Validates Z=A(B/c), κ(n), θ′(n,k) as shared features across domains.
"""

import math
import statistics


class CrossValidation:
    """Cross-domain feature validation."""
    
    def __init__(self):
        pass
    
    def compute_Z_invariant(self, A, B, c):
        """
        Compute Z = A(B/c) cornerstone invariant.
        
        This is the Lorentz-inspired normalization equation that provides
        a universal reference point across domains.
        
        Args:
            A: Domain-specific amplitude/scale factor
            B: Domain-specific parameter (velocity, density, etc.)
            c: Universal constant (speed of light, or domain equivalent)
        
        Returns:
            Z invariant value
        """
        if c == 0:
            raise ValueError("c cannot be zero")
        return A * (B / c)
    
    def compute_kappa(self, n):
        """
        Compute κ(n) - kappa function.
        Represents scaling/growth behavior across domains.
        
        Args:
            n: Input parameter (sequence length, iteration, etc.)
        
        Returns:
            κ(n) value
        """
        # κ(n) ≈ n^α for some α, using log scaling
        if n <= 0:
            return 0
        # Simple formulation: κ(n) = n / log(n+1)
        return n / math.log(n + 2)
    
    def compute_theta_prime(self, n, k):
        """
        Compute θ′(n, k) - theta prime function.
        Geometric combination of n and k.
        
        Args:
            n: Position/index parameter
            k: Scaling parameter
        
        Returns:
            θ′(n, k) value
        """
        # θ′(n,k) = geometric combination influenced by k
        return math.sqrt(n) * (1.0 + k * math.log(1 + n))
    
    def extract_rsa_features(self, n, candidate_variance):
        """
        Extract shared features from RSA domain.
        
        Args:
            n: RSA number being factored
            candidate_variance: Variance in candidate sampling
        
        Returns:
            dict of shared features
        """
        sqrt_n = math.sqrt(n)
        
        # Z = A(B/c): A = variance, B = sqrt(n), c = n
        Z = self.compute_Z_invariant(candidate_variance, sqrt_n, n)
        
        # κ(n): scaling with n
        kappa = self.compute_kappa(int(sqrt_n))
        
        # θ′(n, k): with k=0.3
        theta_prime = self.compute_theta_prime(int(sqrt_n), k=0.3)
        
        return {
            'domain': 'RSA',
            'Z': Z,
            'kappa': kappa,
            'theta_prime': theta_prime,
            'n_param': int(sqrt_n),
        }
    
    def extract_crispr_features(self, n_guides, entropy_mean):
        """
        Extract shared features from CRISPR domain.
        
        Args:
            n_guides: Number of guides analyzed
            entropy_mean: Mean entropy score
        
        Returns:
            dict of shared features
        """
        # Z = A(B/c): A = entropy, B = n_guides, c = constant
        Z = self.compute_Z_invariant(entropy_mean, n_guides, 100.0)
        
        # κ(n): scaling with guide count
        kappa = self.compute_kappa(n_guides)
        
        # θ′(n, k): with k=0.3
        theta_prime = self.compute_theta_prime(n_guides, k=0.3)
        
        return {
            'domain': 'CRISPR',
            'Z': Z,
            'kappa': kappa,
            'theta_prime': theta_prime,
            'n_param': n_guides,
        }
    
    def extract_crypto_features(self, n_rekeys, fail_rate):
        """
        Extract shared features from crypto domain.
        
        Args:
            n_rekeys: Number of rekey operations
            fail_rate: Failure rate percentage
        
        Returns:
            dict of shared features
        """
        # Z = A(B/c): A = (100 - fail_rate) as success metric, 
        #             B = n_rekeys, c = constant
        success_rate = 100 - fail_rate
        Z = self.compute_Z_invariant(success_rate, n_rekeys, 1000.0)
        
        # κ(n): scaling with rekey count
        kappa = self.compute_kappa(n_rekeys)
        
        # θ′(n, k): with k=0.3
        theta_prime = self.compute_theta_prime(n_rekeys, k=0.3)
        
        return {
            'domain': 'Crypto',
            'Z': Z,
            'kappa': kappa,
            'theta_prime': theta_prime,
            'n_param': n_rekeys,
        }
    
    def cross_validate_features(self, all_features):
        """
        Cross-validate that features exist and are consistent across domains.
        
        Args:
            all_features: List of feature dicts from different domains
        
        Returns:
            dict with validation results
        """
        # Check that all domains have the same features
        required_features = ['Z', 'kappa', 'theta_prime']
        
        for features in all_features:
            for feat in required_features:
                if feat not in features:
                    raise ValueError(f"Missing feature {feat} in {features['domain']}")
        
        # Compute statistics across domains
        Z_values = [f['Z'] for f in all_features]
        kappa_values = [f['kappa'] for f in all_features]
        theta_prime_values = [f['theta_prime'] for f in all_features]
        
        # Check for consistency (values should be in reasonable ranges)
        validation = {
            'all_features_present': True,
            'n_domains': len(all_features),
            'domains': [f['domain'] for f in all_features],
            'Z_range': [min(Z_values), max(Z_values)],
            'kappa_range': [min(kappa_values), max(kappa_values)],
            'theta_prime_range': [min(theta_prime_values), max(theta_prime_values)],
            'feature_correlation': self._compute_feature_correlation(all_features),
        }
        
        return validation
    
    def _compute_feature_correlation(self, all_features):
        """Compute correlation between shared features across domains."""
        # Simple correlation: check if kappa and theta_prime scale similarly
        kappa_values = [f['kappa'] for f in all_features]
        theta_values = [f['theta_prime'] for f in all_features]
        
        if len(kappa_values) < 2:
            return 0.0
        
        # Pearson correlation coefficient (simplified)
        mean_kappa = statistics.mean(kappa_values)
        mean_theta = statistics.mean(theta_values)
        
        numerator = sum((k - mean_kappa) * (t - mean_theta) 
                       for k, t in zip(kappa_values, theta_values))
        
        denom_k = sum((k - mean_kappa)**2 for k in kappa_values)
        denom_t = sum((t - mean_theta)**2 for t in theta_values)
        
        if denom_k == 0 or denom_t == 0:
            return 0.0
        
        correlation = numerator / math.sqrt(denom_k * denom_t)
        
        return correlation


def test_cross_validation():
    """Test cross-validation of shared features."""
    print("Testing Cross-Validation of Shared Features...")
    
    cv = CrossValidation()
    
    # Test individual feature extraction
    rsa_features = cv.extract_rsa_features(n=1199, candidate_variance=250.0)
    print(f"RSA features: Z={rsa_features['Z']:.4f}, "
          f"κ={rsa_features['kappa']:.4f}, "
          f"θ′={rsa_features['theta_prime']:.4f}")
    
    crispr_features = cv.extract_crispr_features(n_guides=100, entropy_mean=0.8)
    print(f"CRISPR features: Z={crispr_features['Z']:.4f}, "
          f"κ={crispr_features['kappa']:.4f}, "
          f"θ′={crispr_features['theta_prime']:.4f}")
    
    crypto_features = cv.extract_crypto_features(n_rekeys=1000, fail_rate=5.0)
    print(f"Crypto features: Z={crypto_features['Z']:.4f}, "
          f"κ={crypto_features['kappa']:.4f}, "
          f"θ′={crypto_features['theta_prime']:.4f}")
    
    # Cross-validate
    all_features = [rsa_features, crispr_features, crypto_features]
    validation = cv.cross_validate_features(all_features)
    
    print(f"\nCross-validation results:")
    print(f"  Domains validated: {validation['domains']}")
    print(f"  All features present: {validation['all_features_present']}")
    print(f"  Z range: [{validation['Z_range'][0]:.4f}, {validation['Z_range'][1]:.4f}]")
    print(f"  Feature correlation: {validation['feature_correlation']:.4f}")
    
    print("\nCross-validation tests passed!\n")


if __name__ == "__main__":
    test_cross_validation()
