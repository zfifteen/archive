"""
Universal Invariant Scoring Engine Python Client

Python client library for accessing the Z-score API.
"""

import requests
import json
from typing import Any, Dict, List, Optional, Union
import warnings


class ZScoreAPIClient:
    """
    Python client for Universal Invariant Scoring Engine API.
    
    Provides convenient methods for scoring sequences using Z-invariant mathematics.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the scoring API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ZScoreAPIClient/1.0.0'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API server health.
        
        Returns:
            Health status response
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to API server: {e}")
    
    def score(self, data: Any, data_type: str = 'auto') -> Dict[str, Any]:
        """
        Score a single sequence.
        
        Args:
            data: Input sequence (numerical, biological, or network)
            data_type: Type of data ('numerical', 'biological', 'network', or 'auto')
            
        Returns:
            Scoring result dictionary
        """
        payload = {
            'data': data,
            'data_type': data_type
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/score",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success', False):
                raise ValueError(f"API error: {result.get('error', 'Unknown error')}")
            
            return result['result']
            
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to score sequence: {e}")
    
    def batch_score(self, data_list: List[Any], data_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Score multiple sequences in batch.
        
        Args:
            data_list: List of input sequences
            data_types: Optional list of data types for each sequence
            
        Returns:
            List of scoring results
        """
        payload = {
            'data_list': data_list
        }
        
        if data_types is not None:
            payload['data_types'] = data_types
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/batch_score",
                json=payload,
                timeout=self.timeout * 2  # Longer timeout for batch operations
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success', False):
                raise ValueError(f"API error: {result.get('error', 'Unknown error')}")
            
            return result['results']
            
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to batch score sequences: {e}")
    
    def analyze(self, data: Any, data_type: str = 'auto', 
                include_normalized: bool = False, detailed_metrics: bool = False) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a sequence.
        
        Args:
            data: Input sequence
            data_type: Type of data
            include_normalized: Include normalized sequence in response
            detailed_metrics: Include detailed sub-metrics
            
        Returns:
            Comprehensive analysis result
        """
        payload = {
            'data': data,
            'data_type': data_type,
            'include_normalized': include_normalized,
            'detailed_metrics': detailed_metrics
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/analyze",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success', False):
                raise ValueError(f"API error: {result.get('error', 'Unknown error')}")
            
            return result['analysis']
            
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to analyze sequence: {e}")
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and documentation.
        
        Returns:
            API information dictionary
        """
        try:
            response = self.session.get(f"{self.base_url}/api/info", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to get API info: {e}")
    
    def score_numerical(self, data: Union[List[float], List[int]]) -> float:
        """
        Convenience method to score numerical data and return just the Z-invariant score.
        
        Args:
            data: Numerical sequence
            
        Returns:
            Z-invariant score
        """
        result = self.score(data, 'numerical')
        return result['z_invariant_score']
    
    def score_biological(self, sequence: str) -> float:
        """
        Convenience method to score biological sequence and return just the Z-invariant score.
        
        Args:
            sequence: DNA, RNA, or protein sequence string
            
        Returns:
            Z-invariant score
        """
        result = self.score(sequence, 'biological')
        return result['z_invariant_score']
    
    def score_network(self, adjacency_matrix: Union[List[List], Dict]) -> float:
        """
        Convenience method to score network data and return just the Z-invariant score.
        
        Args:
            adjacency_matrix: Network adjacency matrix or dict with 'adjacency_matrix' key
            
        Returns:
            Z-invariant score
        """
        result = self.score(adjacency_matrix, 'network')
        return result['z_invariant_score']
    
    def detect_anomalies(self, data: Any, data_type: str = 'auto', threshold: float = 0.5) -> Dict[str, Any]:
        """
        Detect anomalies in a sequence.
        
        Args:
            data: Input sequence
            data_type: Type of data
            threshold: Anomaly detection threshold (0-1)
            
        Returns:
            Anomaly detection results
        """
        analysis = self.analyze(data, data_type, detailed_metrics=True)
        
        anomaly_score = analysis.get('anomaly_scores', {}).get('composite_anomaly_score', 0.0)
        has_anomalies = anomaly_score > threshold
        
        return {
            'has_anomalies': has_anomalies,
            'anomaly_score': anomaly_score,
            'threshold': threshold,
            'detailed_scores': analysis.get('anomaly_scores', {}),
            'metadata': analysis.get('metadata', {})
        }
    
    def benchmark_sequences(self, sequences: List[Any], data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Benchmark multiple sequences against each other.
        
        Args:
            sequences: List of sequences to benchmark
            data_types: Optional data types for each sequence
            
        Returns:
            Benchmarking results with rankings and statistics
        """
        results = self.batch_score(sequences, data_types)
        
        # Extract scores and calculate statistics
        scores = []
        valid_results = []
        
        for i, result in enumerate(results):
            if 'error' not in result:
                score = result.get('z_invariant_score', 0.0)
                scores.append(score)
                valid_results.append({
                    'index': i,
                    'score': score,
                    'metadata': result.get('metadata', {}),
                    'enhancement_factor': result.get('density_metrics', {}).get('enhancement_factor', 1.0)
                })
        
        if not scores:
            return {'error': 'No valid sequences to benchmark'}
        
        # Sort by score (descending)
        valid_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Calculate statistics
        import numpy as np
        scores_array = np.array(scores)
        
        return {
            'rankings': valid_results,
            'statistics': {
                'mean_score': float(np.mean(scores_array)),
                'std_score': float(np.std(scores_array)),
                'min_score': float(np.min(scores_array)),
                'max_score': float(np.max(scores_array)),
                'median_score': float(np.median(scores_array))
            },
            'total_sequences': len(sequences),
            'valid_sequences': len(valid_results),
            'errors': len(sequences) - len(valid_results)
        }
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience functions for direct usage
def score_sequence(data: Any, data_type: str = 'auto', api_url: str = "http://localhost:5000") -> Dict[str, Any]:
    """
    Score a single sequence using the API.
    
    Args:
        data: Input sequence
        data_type: Type of data
        api_url: API server URL
        
    Returns:
        Scoring result
    """
    with ZScoreAPIClient(api_url) as client:
        return client.score(data, data_type)


def batch_score_sequences(data_list: List[Any], data_types: Optional[List[str]] = None, 
                         api_url: str = "http://localhost:5000") -> List[Dict[str, Any]]:
    """
    Score multiple sequences in batch using the API.
    
    Args:
        data_list: List of input sequences
        data_types: Optional data types
        api_url: API server URL
        
    Returns:
        List of scoring results
    """
    with ZScoreAPIClient(api_url) as client:
        return client.batch_score(data_list, data_types)