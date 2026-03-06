import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# from scipy.stats import zeta  # Not needed for this analysis

# Topological embedding methods for prime gaps
class PrimeGapTopology:
    def __init__(self, max_prime=1000):
        self.max_prime = max_prime
        self.primes = self.sieve_primes()
        self.gaps = np.diff(self.primes)
    
    def sieve_primes(self):
        """Sieve of Eratosthenes for primes"""
        sieve = [True] * (self.max_prime + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(self.max_prime**0.5) + 1):
            if sieve[i]:
                sieve[i*i::i] = [False] * len(sieve[i*i::i])
        return np.array([i for i, is_prime in enumerate(sieve) if is_prime])
    
    # Method 1: Helical embedding (building on gunit3.py)
    def helical_embedding(self, alpha=0.1003033):
        """Enhanced helical embedding based on gunit3.py frequency"""
        gap_norm = self.gaps / self.gaps.max()
        t = np.arange(len(self.gaps))
        # Use the HELIX_FREQ from gunit3.py for consistency
        x = np.cos(alpha * t) * gap_norm
        y = np.sin(alpha * t) * gap_norm
        z = t / len(t)
        return x, y, z
    
    # Method 2: Möbius strip embedding
    def mobius_embedding(self):
        """Map prime gaps onto a Möbius strip topology"""
        gap_norm = self.gaps / self.gaps.max()
        t = np.linspace(0, 2*np.pi, len(self.gaps))
        u = t
        a = gap_norm
        # Möbius strip parametrization
        x = (a + a*np.cos(u/2)*np.cos(u))
        y = (a + a*np.cos(u/2)*np.sin(u))
        z = a*np.sin(u/2)
        return x, y, z
    
    # Method 3: Knot-like embedding (torus knot)
    def knot_embedding(self, p=3, q=2):
        """Embed gaps in a torus knot configuration"""
        gap_norm = self.gaps / self.gaps.max()
        t = np.linspace(0, 2*np.pi, len(self.gaps))
        # Torus knot parameters
        R = 1 + 0.5 * gap_norm  # Major radius varies with gap size
        r = 0.3 * gap_norm      # Minor radius varies with gap size
        x = (R + r*np.cos(q*t)) * np.cos(p*t)
        y = (R + r*np.cos(q*t)) * np.sin(p*t)
        z = r*np.sin(q*t)
        return x, y, z
    
    # Method 4: Hyperbolic embedding
    def hyperbolic_embedding(self):
        """Map gaps onto hyperboloid of one sheet"""
        gap_norm = self.gaps / self.gaps.max()
        # Avoid division by zero and ensure valid arctanh domain
        gap_norm = np.clip(gap_norm, 0.001, 0.999)
        t = np.linspace(0, 2*np.pi, len(self.gaps))
        
        # Hyperbolic coordinates
        rho = np.arctanh(gap_norm)
        phi = t
        theta = 2*t
        
        # Hyperboloid parametrization
        x = rho * np.sinh(phi) * np.cos(theta)
        y = rho * np.sinh(phi) * np.sin(theta)
        z = rho * np.cosh(phi)
        return x, y, z
    
    # Method 5: Spherical embedding with gap-dependent radius
    def spherical_embedding(self):
        """Map gaps onto spherical surface with varying radius"""
        gap_norm = self.gaps / self.gaps.max()
        n_gaps = len(self.gaps)
        
        # Distribute points on sphere using golden spiral
        indices = np.arange(0, n_gaps, dtype=float) + 0.5
        theta = np.arccos(1 - 2*indices/n_gaps)  # Inclination
        phi = np.pi * (1 + 5**0.5) * indices     # Azimuth (golden angle)
        
        # Radius varies with gap size
        r = 1 + gap_norm
        
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return x, y, z
    
    # Method 6: Klein bottle embedding
    def klein_bottle_embedding(self):
        """Embed gaps on Klein bottle surface"""
        gap_norm = self.gaps / self.gaps.max()
        n_gaps = len(self.gaps)
        
        u = np.linspace(0, 2*np.pi, n_gaps)
        v = np.linspace(0, 2*np.pi, n_gaps)
        
        # Scale parameters with gap size
        a = 1 + gap_norm * 0.5
        
        # Klein bottle parametrization
        x = (a + np.cos(u/2)*np.sin(v) - np.sin(u/2)*np.sin(2*v)) * np.cos(u)
        y = (a + np.cos(u/2)*np.sin(v) - np.sin(u/2)*np.sin(2*v)) * np.sin(u)
        z = np.sin(u/2)*np.sin(v) + np.cos(u/2)*np.sin(2*v)
        return x, y, z
    
    def visualize_embedding(self, method_name, save_path=None):
        """Visualize a specific embedding method"""
        method_map = {
            'helical': self.helical_embedding,
            'mobius': self.mobius_embedding,
            'knot': self.knot_embedding,
            'hyperbolic': self.hyperbolic_embedding,
            'spherical': self.spherical_embedding,
            'klein': self.klein_bottle_embedding
        }
        
        if method_name not in method_map:
            raise ValueError(f"Unknown method: {method_name}")
        
        try:
            x, y, z = method_map[method_name]()
            
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Color by gap size for better visualization
            scatter = ax.scatter(x, y, z, c=self.gaps, cmap='viridis', 
                               s=50, alpha=0.7)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'{method_name.title()} Embedding of Prime Gaps')
            
            # Add colorbar
            plt.colorbar(scatter, ax=ax, label='Gap Size')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig, ax
            
        except Exception as e:
            print(f"Error in {method_name} embedding: {e}")
            return None, None