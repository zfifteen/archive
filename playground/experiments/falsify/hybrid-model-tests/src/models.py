import numpy as np
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
try:
    from arch import arch_model
    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False
    print("Warning: arch package not available, GARCH model will be simplified")
import warnings
warnings.filterwarnings('ignore')

class BaseModel:
    """Base class for hybrid models"""
    def __init__(self, name):
        self.name = name

    def simulate(self, params, n_samples):
        """Generate synthetic data given parameters"""
        raise NotImplementedError

    def fit(self, target_stats):
        """Fit parameters to match target statistics"""
        raise NotImplementedError

class LognormalARMA(BaseModel):
    """Model 1: Lognormal ARMA(1,1)
    Δ_n = exp(X_n)
    X_n = φ X_{n-1} + ε_n + θ ε_{n-1}
    ε_n ~ N(0, σ²)
    """
    def __init__(self):
        super().__init__("Lognormal ARMA(1,1)")

    def simulate(self, params, n_samples):
        phi, theta, sigma = params
        # Generate ARMA(1,1) process
        np.random.seed(42)  # For reproducibility
        ar = [1, -phi] if phi != 0 else [1]
        ma = [1, theta] if theta != 0 else [1]
        model = ARIMA(np.zeros(n_samples), order=(1, 0, 1), seasonal_order=(0, 0, 0, 0))
        model.initialize_approximate_diffuse()
        # Manually set parameters
        X = np.zeros(n_samples)
        eps = np.random.normal(0, sigma, n_samples)
        for t in range(1, n_samples):
            X[t] = phi * X[t-1] + eps[t] + theta * eps[t-1]
        # Apply lognormal transformation
        gaps = np.exp(X)
        return gaps

    def fit(self, target_stats):
        # Simple grid search for parameters
        phi_range = np.linspace(-0.9, 0.9, 10)
        theta_range = np.linspace(-0.9, 0.9, 10)
        sigma_range = np.linspace(0.1, 2.0, 10)

        best_params = None
        best_error = float('inf')

        for phi in phi_range:
            for theta in theta_range:
                for sigma in sigma_range:
                    try:
                        synthetic = self.simulate((phi, theta, sigma), 10000)
                        # Compute error against target mean and acf
                        error = abs(np.mean(synthetic) - target_stats['mean']) + \
                               abs(np.std(synthetic) - target_stats['std'])
                        if 'acf1' in target_stats:
                            acf1 = np.corrcoef(synthetic[:-1], synthetic[1:])[0,1]
                            error += abs(acf1 - target_stats['acf1'])
                        if error < best_error:
                            best_error = error
                            best_params = (phi, theta, sigma)
                    except:
                        continue
        return best_params

class ExponentialDrift(BaseModel):
    """Model 2: Exponential + Drift
    Δ_n = λ + β n + exp(ε_n)
    ε_n ~ N(0, σ²)
    """
    def __init__(self):
        super().__init__("Exponential + Drift")

    def simulate(self, params, n_samples):
        lam, beta, sigma = params
        np.random.seed(42)
        n = np.arange(1, n_samples + 1)
        eps = np.random.normal(0, sigma, n_samples)
        gaps = lam + beta * n + np.exp(eps)
        return gaps

    def fit(self, target_stats):
        # Fit using least squares
        # This is simplified - in practice would use optimization
        lam = target_stats['mean'] - 0.5 * target_stats['std']**2  # Approximation
        beta = 0.0  # Assume no drift
        sigma = target_stats['std']
        return (lam, beta, sigma)

class FractionalGNLognormal(BaseModel):
    """Model 3: Fractional Gaussian noise + Lognormal base
    Δ_n = exp(μ + fGn(H))
    """
    def __init__(self):
        super().__init__("Fractional GN + Lognormal")

    def simulate(self, params, n_samples):
        mu, H = params
        np.random.seed(42)
        # Simplified fGn generation (not true fractional)
        # In practice, would use more sophisticated method
        noise = np.random.normal(0, 1, n_samples)
        # Apply Hurst exponent effect approximately
        if H > 0.5:
            # Long-range dependence approximation
            for i in range(1, n_samples):
                noise[i] += 0.5 * noise[i-1]
        gaps = np.exp(mu + noise)
        return gaps

    def fit(self, target_stats):
        mu = np.log(target_stats['mean']) - 0.5 * target_stats['std']**2
        H = 0.7  # Typical value for long-range dependence
        return (mu, H)

class GARCHLognormal(BaseModel):
    """Model 4: GARCH(1,1) + Lognormal
    X_n = μ + σ_n ε_n
    σ_n² = ω + α (X_{n-1} - μ)² + β σ_{n-1}²
    Δ_n = exp(X_n)
    """
    def __init__(self):
        super().__init__("GARCH(1,1) + Lognormal")

    def simulate(self, params, n_samples):
        mu, omega, alpha, beta = params
        np.random.seed(42)
        # Simplified GARCH simulation
        X = np.zeros(n_samples)
        sigma_sq = np.ones(n_samples) * omega
        eps = np.random.normal(0, 1, n_samples)

        for t in range(1, n_samples):
            sigma_sq[t] = omega + alpha * (X[t-1] - mu)**2 + beta * sigma_sq[t-1]
            X[t] = mu + np.sqrt(sigma_sq[t]) * eps[t]

        gaps = np.exp(X)
        return gaps

    def fit(self, target_stats):
        # Simplified parameter estimation
        mu = np.log(target_stats['mean']) - 0.5 * target_stats['std']**2
        omega = target_stats['std']**2 * 0.1
        alpha = 0.1
        beta = 0.8
        return (mu, omega, alpha, beta)

class CorrelatedCramer(BaseModel):
    """Model 5: Cramér model with correlated gaps
    Δ_n ~ Poisson(λ) with gaps correlated via Cov(Δ_n, Δ_{n+k}) = ρ^k
    """
    def __init__(self):
        super().__init__("Correlated Cramér")

    def simulate(self, params, n_samples):
        lam, rho = params
        np.random.seed(42)
        # Generate correlated exponential gaps
        gaps = np.random.exponential(1/lam, n_samples)
        # Add correlation by AR(1) transformation
        for i in range(1, n_samples):
            gaps[i] = rho * gaps[i-1] + (1-rho) * gaps[i]
        return gaps

    def fit(self, target_stats):
        lam = 1 / target_stats['mean']
        rho = target_stats.get('acf1', 0.1)
        return (lam, rho)

class AdditiveDecomposition(BaseModel):
    """Model 6: Additive decomposition
    Δ_n = Trend(n) + Seasonal(n) + Noise(n)
    Trend(n) = a + b ln(n)
    Seasonal(n) = A sin(2π n / P)
    Noise(n) ~ Lognormal(μ, σ)
    """
    def __init__(self):
        super().__init__("Additive Decomposition")

    def simulate(self, params, n_samples):
        a, b, A, P, mu, sigma = params
        np.random.seed(42)
        n = np.arange(1, n_samples + 1)
        trend = a + b * np.log(n)
        seasonal = A * np.sin(2 * np.pi * n / P)
        noise = np.random.lognormal(mu, sigma, n_samples)
        gaps = trend + seasonal + noise
        return gaps

    def fit(self, target_stats):
        # Simplified fitting
        a = target_stats['mean'] * 0.5
        b = 0.0
        A = target_stats['std'] * 0.1
        P = 100  # Arbitrary period
        mu = np.log(target_stats['mean']) - 0.5 * target_stats['std']**2
        sigma = target_stats['std']
        return (a, b, A, P, mu, sigma)
