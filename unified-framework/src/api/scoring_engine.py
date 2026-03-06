"""
Universal Invariant Scoring Engine Core

Provides Z-invariant scoring, density analysis, and anomaly detection
for arbitrary sequences using the Z Framework's mathematical foundations.
"""

import numpy as np
import mpmath as mp
from typing import List, Dict, Any, Union, Optional
from abc import ABC, abstractmethod

# Set high precision for mathematical operations
mp.mp.dps = 50

# Import Z Framework core components
try:
    from ..core.domain import DiscreteZetaShift
    from ..core.axioms import universal_invariance, theta_prime, curvature
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.domain import DiscreteZetaShift
    from core.axioms import universal_invariance, theta_prime, curvature

PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)


class DataNormalizer(ABC):
    """Abstract base class for data normalization strategies."""
    
    @abstractmethod
    def normalize(self, data: Any) -> List[float]:
        """Convert input data to normalized numerical sequence."""
        pass
    
    @abstractmethod
    def get_metadata(self, data: Any) -> Dict[str, Any]:
        """Extract metadata about the input data."""
        pass


class NumericalNormalizer(DataNormalizer):
    """Normalizer for numerical sequences."""
    
    def normalize(self, data: Union[List, np.ndarray]) -> List[float]:
        """Normalize numerical data to [0, 1] range."""
        arr = np.array(data, dtype=float)
        if len(arr) == 0:
            return []
        
        # Handle constant sequences
        if np.max(arr) == np.min(arr):
            return [0.5] * len(arr)
            
        # Min-max normalization
        normalized = (arr - np.min(arr)) / (np.max(arr) - np.min(arr))
        return normalized.tolist()
    
    def get_metadata(self, data: Union[List, np.ndarray]) -> Dict[str, Any]:
        """Extract numerical sequence metadata."""
        arr = np.array(data, dtype=float)
        return {
            'type': 'numerical',
            'length': len(arr),
            'mean': float(np.mean(arr)) if len(arr) > 0 else 0,
            'std': float(np.std(arr)) if len(arr) > 0 else 0,
            'min': float(np.min(arr)) if len(arr) > 0 else 0,
            'max': float(np.max(arr)) if len(arr) > 0 else 0
        }


class BiologicalNormalizer(DataNormalizer):
    """Normalizer for biological sequences (DNA, RNA, protein)."""
    
    # Standard encoding maps
    DNA_MAP = {'A': 0.0, 'T': 0.25, 'G': 0.5, 'C': 0.75, 'N': 0.125}
    RNA_MAP = {'A': 0.0, 'U': 0.25, 'G': 0.5, 'C': 0.75, 'N': 0.125}
    AMINO_ACID_MAP = {
        'A': 0.05, 'R': 0.10, 'N': 0.15, 'D': 0.20, 'C': 0.25, 'Q': 0.30,
        'E': 0.35, 'G': 0.40, 'H': 0.45, 'I': 0.50, 'L': 0.55, 'K': 0.60,
        'M': 0.65, 'F': 0.70, 'P': 0.75, 'S': 0.80, 'T': 0.85, 'W': 0.90,
        'Y': 0.95, 'V': 1.00, 'X': 0.5  # X for unknown
    }
    
    def normalize(self, data: str) -> List[float]:
        """Convert biological sequence to numerical values."""
        sequence = data.upper().strip()
        
        # Detect sequence type
        if self._is_dna(sequence):
            mapping = self.DNA_MAP
        elif self._is_rna(sequence):
            mapping = self.RNA_MAP
        else:
            mapping = self.AMINO_ACID_MAP
            
        # Convert to numerical values
        return [mapping.get(char, 0.5) for char in sequence]
    
    def get_metadata(self, data: str) -> Dict[str, Any]:
        """Extract biological sequence metadata."""
        sequence = data.upper().strip()
        
        if self._is_dna(sequence):
            seq_type = 'DNA'
            composition = {base: sequence.count(base) for base in 'ATGC'}
        elif self._is_rna(sequence):
            seq_type = 'RNA'
            composition = {base: sequence.count(base) for base in 'AUGC'}
        else:
            seq_type = 'protein'
            composition = {aa: sequence.count(aa) for aa in self.AMINO_ACID_MAP.keys()}
            
        return {
            'type': 'biological',
            'sequence_type': seq_type,
            'length': len(sequence),
            'composition': composition,
            'gc_content': self._calculate_gc_content(sequence) if seq_type in ['DNA', 'RNA'] else None
        }
    
    def _is_dna(self, sequence: str) -> bool:
        """Check if sequence is DNA."""
        dna_chars = set('ATGCN')
        return all(char in dna_chars for char in sequence)
    
    def _is_rna(self, sequence: str) -> bool:
        """Check if sequence is RNA."""
        rna_chars = set('AUGCN')
        return 'U' in sequence and 'T' not in sequence and all(char in rna_chars for char in sequence)
    
    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content for DNA/RNA sequences."""
        gc_count = sequence.count('G') + sequence.count('C')
        total_count = len([c for c in sequence if c in 'ATGCU'])
        return gc_count / total_count if total_count > 0 else 0.0


class NetworkNormalizer(DataNormalizer):
    """Normalizer for network/graph data."""
    
    def normalize(self, data: Union[List[List], Dict]) -> List[float]:
        """Convert network data to numerical sequence based on centrality measures."""
        if isinstance(data, dict) and 'adjacency_matrix' in data:
            matrix = np.array(data['adjacency_matrix'])
        elif isinstance(data, list):
            matrix = np.array(data)
        else:
            raise ValueError("Network data must be adjacency matrix or dict with 'adjacency_matrix' key")
        
        # Calculate degree centrality as primary metric
        degrees = np.sum(matrix, axis=1)
        
        # Normalize to [0, 1]
        if np.max(degrees) == np.min(degrees):
            return [0.5] * len(degrees)
        
        normalized = (degrees - np.min(degrees)) / (np.max(degrees) - np.min(degrees))
        return normalized.tolist()
    
    def get_metadata(self, data: Union[List[List], Dict]) -> Dict[str, Any]:
        """Extract network metadata."""
        if isinstance(data, dict) and 'adjacency_matrix' in data:
            matrix = np.array(data['adjacency_matrix'])
        else:
            matrix = np.array(data)
            
        n_nodes = matrix.shape[0]
        n_edges = np.sum(matrix) // 2 if np.allclose(matrix, matrix.T) else np.sum(matrix)
        density = n_edges / (n_nodes * (n_nodes - 1) / 2) if n_nodes > 1 else 0
        
        return {
            'type': 'network',
            'n_nodes': int(n_nodes),
            'n_edges': int(n_edges),
            'density': float(density),
            'is_directed': not np.allclose(matrix, matrix.T)
        }


class UniversalScoringEngine:
    """
    Universal Invariant Scoring Engine using Z Framework mathematics.
    
    Computes Z-invariant scores, density analysis, and anomaly detection
    for arbitrary input sequences.
    """
    
    def __init__(self):
        """Initialize the scoring engine."""
        self.normalizers = {
            'numerical': NumericalNormalizer(),
            'biological': BiologicalNormalizer(),
            'network': NetworkNormalizer()
        }
    
    def score_sequence(self, data: Any, data_type: str = 'auto') -> Dict[str, Any]:
        """
        Compute comprehensive Z-invariant scores for input data.
        
        Args:
            data: Input sequence (numerical, biological, or network)
            data_type: Type of data ('numerical', 'biological', 'network', or 'auto')
            
        Returns:
            Dict containing scores, metadata, and analysis results
        """
        # Auto-detect data type if needed
        if data_type == 'auto':
            data_type = self._detect_data_type(data)
        
        if data_type not in self.normalizers:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        # Normalize data
        normalizer = self.normalizers[data_type]
        normalized_seq = normalizer.normalize(data)
        metadata = normalizer.get_metadata(data)
        
        if len(normalized_seq) == 0:
            return self._empty_result(metadata)
        
        # Compute Z-invariant scores
        z_scores = self._compute_z_invariant_scores(normalized_seq)
        
        # Compute density metrics
        density_metrics = self._compute_density_metrics(normalized_seq)
        
        # Compute anomaly scores
        anomaly_scores = self._compute_anomaly_scores(normalized_seq)
        
        return {
            'metadata': metadata,
            'z_invariant_score': z_scores['composite_score'],
            'z_scores': z_scores,
            'density_metrics': density_metrics,
            'anomaly_scores': anomaly_scores,
            'normalized_sequence': normalized_seq[:100],  # Limit for response size
            'sequence_length': len(normalized_seq)
        }
    
    def batch_score(self, data_list: List[Any], data_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Score multiple sequences in batch.
        
        Args:
            data_list: List of input sequences
            data_types: List of data types (optional, uses auto-detection if None)
            
        Returns:
            List of scoring results
        """
        if data_types is None:
            data_types = ['auto'] * len(data_list)
        
        results = []
        for i, (data, dtype) in enumerate(zip(data_list, data_types)):
            try:
                result = self.score_sequence(data, dtype)
                result['batch_index'] = i
                results.append(result)
            except Exception as e:
                results.append({
                    'batch_index': i,
                    'error': str(e),
                    'metadata': {'type': 'error'}
                })
        
        return results
    
    def _detect_data_type(self, data: Any) -> str:
        """Auto-detect data type from input."""
        if isinstance(data, str):
            return 'biological'
        elif isinstance(data, (list, np.ndarray)):
            # Check if it's a matrix (network data)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], (list, np.ndarray)):
                return 'network'
            return 'numerical'
        elif isinstance(data, dict) and 'adjacency_matrix' in data:
            return 'network'
        else:
            return 'numerical'
    
    def _compute_z_invariant_scores(self, sequence: List[float]) -> Dict[str, float]:
        """Compute Z-invariant scores using DiscreteZetaShift."""
        scores = {}
        
        # Convert to integers for DiscreteZetaShift (scaled by 1000 for precision)
        int_sequence = [max(1, int(x * 1000)) for x in sequence[:100]]  # Limit for performance
        
        try:
            # Compute Z-scores for first few elements
            z_values = []
            for i, n in enumerate(int_sequence[:20]):  # Limit computation
                try:
                    dz = DiscreteZetaShift(n)
                    z_val = float(dz.compute_z())
                    z_values.append(z_val)
                except Exception:
                    continue
            
            if z_values:
                scores['mean_z'] = np.mean(z_values)
                scores['std_z'] = np.std(z_values)
                scores['max_z'] = np.max(z_values)
                scores['min_z'] = np.min(z_values)
            else:
                scores['mean_z'] = 0.0
                scores['std_z'] = 0.0
                scores['max_z'] = 0.0
                scores['min_z'] = 0.0
            
            # Compute universal invariance score
            if len(sequence) >= 2:
                ui_score = float(universal_invariance(sequence[0], sequence[1]))
                scores['universal_invariance'] = ui_score
            else:
                scores['universal_invariance'] = 0.0
            
            # Compute composite score
            scores['composite_score'] = (scores['mean_z'] + scores['universal_invariance']) / 2
            
        except Exception as e:
            # Fallback scoring
            scores = {
                'mean_z': 0.0,
                'std_z': 0.0,
                'max_z': 0.0,
                'min_z': 0.0,
                'universal_invariance': 0.0,
                'composite_score': 0.0,
                'error': str(e)
            }
        
        return scores
    
    def _compute_density_metrics(self, sequence: List[float]) -> Dict[str, float]:
        """Compute density-based metrics."""
        arr = np.array(sequence)
        
        # Basic density metrics
        density = len(arr) / (np.max(arr) - np.min(arr) + 1e-10)
        
        # Cluster density using golden ratio transformation
        try:
            phi_transformed = [float(theta_prime(x, mp.mpf(0.3))) for x in sequence[:50]]
            cluster_variance = np.var(phi_transformed)
        except Exception:
            cluster_variance = np.var(arr)
        
        # Prime-like density (count elements near "prime-like" positions)
        prime_like_positions = [x for x in sequence if x > 0.1 and x % 0.618 < 0.1]
        prime_density = len(prime_like_positions) / len(sequence)
        
        return {
            'basic_density': float(density),
            'cluster_variance': float(cluster_variance),
            'prime_density': float(prime_density),
            'enhancement_factor': float(1.0 + prime_density * 0.15)  # 15% enhancement at k*≈0.3
        }
    
    def _compute_anomaly_scores(self, sequence: List[float]) -> Dict[str, float]:
        """Compute anomaly detection scores."""
        arr = np.array(sequence)
        
        # Statistical anomalies
        mean_val = np.mean(arr)
        std_val = np.std(arr)
        z_scores = np.abs((arr - mean_val) / (std_val + 1e-10))
        statistical_anomalies = np.sum(z_scores > 2.0) / len(arr)
        
        # Geometric anomalies using curvature
        if len(sequence) >= 3:
            curvatures = []
            for i in range(1, len(sequence) - 1):
                try:
                    # Simple curvature approximation
                    curvature = abs(sequence[i-1] - 2*sequence[i] + sequence[i+1])
                    curvatures.append(curvature)
                except Exception:
                    continue
            
            if curvatures:
                curvature_anomalies = np.sum(np.array(curvatures) > np.percentile(curvatures, 90)) / len(curvatures)
            else:
                curvature_anomalies = 0.0
        else:
            curvature_anomalies = 0.0
        
        # Frame shift anomalies (using discrete domain concepts)
        frame_shifts = np.diff(arr)
        frame_anomalies = np.sum(np.abs(frame_shifts) > 0.1) / len(frame_shifts) if len(frame_shifts) > 0 else 0.0
        
        return {
            'statistical_anomalies': float(statistical_anomalies),
            'curvature_anomalies': float(curvature_anomalies),
            'frame_anomalies': float(frame_anomalies),
            'composite_anomaly_score': float((statistical_anomalies + curvature_anomalies + frame_anomalies) / 3)
        }
    
    def _empty_result(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Return empty result for invalid input."""
        return {
            'metadata': metadata,
            'z_invariant_score': 0.0,
            'z_scores': {'error': 'Empty sequence'},
            'density_metrics': {'error': 'Empty sequence'},
            'anomaly_scores': {'error': 'Empty sequence'},
            'normalized_sequence': [],
            'sequence_length': 0
        }


# Factory function for easy access
def create_scoring_engine() -> UniversalScoringEngine:
    """Create and return a new UniversalScoringEngine instance."""
    return UniversalScoringEngine()