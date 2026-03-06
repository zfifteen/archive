#!/usr/bin/env python3
"""
Prime Geodesic API for External Integration

RESTful API providing access to prime geodesic search engine functionality
for external mathematical datasets and research applications.

Features:
- RESTful API endpoints for coordinate generation and analysis
- Integration with mathematical datasets (OEIS, prime databases)
- Batch processing capabilities for large sequences
- Real-time anomaly detection and clustering
- Comprehensive documentation and examples
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import numpy as np
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict
import time
import hashlib
from functools import wraps
import requests

from applications.prime_geodesic_search import PrimeGeodesicSearchEngine, GeodesicPoint, SearchResult

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Global engine instance
engine = PrimeGeodesicSearchEngine(k_optimal=0.3)

# API rate limiting and caching
request_cache = {}
rate_limit_data = {}

def rate_limit(max_requests_per_minute=60):
    """Rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            current_time = time.time()
            
            if client_ip not in rate_limit_data:
                rate_limit_data[client_ip] = []
            
            # Clean old requests (older than 1 minute)
            rate_limit_data[client_ip] = [
                req_time for req_time in rate_limit_data[client_ip] 
                if current_time - req_time < 60
            ]
            
            if len(rate_limit_data[client_ip]) >= max_requests_per_minute:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'max_requests': max_requests_per_minute,
                    'time_window': '1 minute'
                }), 429
            
            rate_limit_data[client_ip].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_result(cache_key: str, result: Any, ttl: int = 300):
    """Cache result with TTL."""
    request_cache[cache_key] = {
        'result': result,
        'timestamp': time.time(),
        'ttl': ttl
    }

def get_cached_result(cache_key: str) -> Optional[Any]:
    """Get cached result if not expired."""
    if cache_key in request_cache:
        cached = request_cache[cache_key]
        if time.time() - cached['timestamp'] < cached['ttl']:
            return cached['result']
        else:
            del request_cache[cache_key]
    return None

def validate_range(start: int, end: int, max_range: int = 10000):
    """Validate integer range parameters."""
    if not isinstance(start, int) or not isinstance(end, int):
        raise ValueError("Start and end must be integers")
    if start >= end:
        raise ValueError("Start must be less than end")
    if end - start > max_range:
        raise ValueError(f"Range too large. Maximum range: {max_range}")
    if start < 1:
        raise ValueError("Start must be positive")

def geodesic_point_to_dict(point: GeodesicPoint) -> Dict[str, Any]:
    """Convert GeodesicPoint to dictionary for JSON serialization."""
    return {
        'n': point.n,
        'coordinates_3d': {
            'x': point.coordinates_3d[0],
            'y': point.coordinates_3d[1], 
            'z': point.coordinates_3d[2]
        },
        'coordinates_5d': {
            'x': point.coordinates_5d[0],
            'y': point.coordinates_5d[1],
            'z': point.coordinates_5d[2],
            'w': point.coordinates_5d[3],
            'u': point.coordinates_5d[4]
        },
        'is_prime': point.is_prime,
        'curvature': point.curvature,
        'density_enhancement': point.density_enhancement,
        'cluster_id': point.cluster_id,
        'geodesic_type': point.geodesic_type
    }

@app.route('/api/v1', methods=['GET'])
def api_info():
    """Get API information and available endpoints."""
    return jsonify({
        'name': 'Prime Geodesic Search Engine API',
        'version': '1.0.0',
        'description': 'RESTful API for prime geodesic analysis using θ\'(n,k) transformation',
        'framework': 'Z Framework with k* ≈ 0.3 optimal curvature',
        'endpoints': {
            'coordinates': {
                'url': '/api/v1/coordinates',
                'methods': ['POST'],
                'description': 'Generate geodesic coordinates for integer sequences'
            },
            'search': {
                'url': '/api/v1/search',
                'methods': ['POST'],
                'description': 'Search for primes/patterns with specific criteria'
            },
            'clusters': {
                'url': '/api/v1/clusters',
                'methods': ['POST'],
                'description': 'Find prime clusters in geodesic space'
            },
            'anomalies': {
                'url': '/api/v1/anomalies',
                'methods': ['POST'],
                'description': 'Detect gaps and anomalies in sequences'
            },
            'statistics': {
                'url': '/api/v1/statistics',
                'methods': ['POST'],
                'description': 'Generate statistical analysis reports'
            },
            'validate': {
                'url': '/api/v1/validate',
                'methods': ['POST'],
                'description': 'Validate Z Framework predictions'
            },
            'batch': {
                'url': '/api/v1/batch',
                'methods': ['POST'],
                'description': 'Batch processing for large datasets'
            }
        },
        'rate_limit': '60 requests per minute',
        'cache_ttl': '5 minutes for computation results'
    })

@app.route('/api/v1/coordinates', methods=['POST'])
@rate_limit(max_requests_per_minute=30)
def generate_coordinates():
    """
    Generate geodesic coordinates for integer sequences.
    
    Request body:
    {
        "start": 2,
        "end": 100,
        "step": 1,
        "include_metadata": true
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        start = data.get('start', 2)
        end = data.get('end', 100)
        step = data.get('step', 1)
        include_metadata = data.get('include_metadata', True)
        
        validate_range(start, end, max_range=1000)
        
        # Check cache
        cache_key = f"coords_{start}_{end}_{step}"
        cached_result = get_cached_result(cache_key)
        if cached_result:
            return jsonify(cached_result)
        
        # Generate coordinates
        points = engine.generate_sequence_coordinates(start, end, step)
        
        # Convert to JSON-serializable format
        result = {
            'success': True,
            'parameters': {
                'start': start,
                'end': end,
                'step': step,
                'k_optimal': engine.k_optimal,
                'phi': engine.phi
            },
            'summary': {
                'total_points': len(points),
                'prime_count': len([p for p in points if p.is_prime]),
                'range_span': end - start
            },
            'coordinates': [geodesic_point_to_dict(p) for p in points]
        }
        
        if include_metadata:
            result['metadata'] = {
                'computation_time': time.time(),
                'framework_version': '1.0.0',
                'mathematical_basis': 'θ\'(n,k) = φ·{n/φ}^k with k* ≈ 0.3'
            }
        
        # Cache result
        cache_result(cache_key, result, ttl=300)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/search', methods=['POST'])
@rate_limit(max_requests_per_minute=20)
def search_patterns():
    """
    Search for patterns with specific criteria.
    
    Request body:
    {
        "start": 2,
        "end": 1000,
        "criteria": {
            "primes_only": true,
            "curvature_range": [0.1, 2.0],
            "min_density_enhancement": 5.0,
            "coordinate_bounds_3d": {
                "x_min": -1.0, "x_max": 1.0,
                "y_min": -1.0, "y_max": 1.0,
                "z_min": 0.0, "z_max": 1.0
            }
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        start = data.get('start', 2)
        end = data.get('end', 100)
        criteria = data.get('criteria', {})
        
        validate_range(start, end, max_range=5000)
        
        # Perform search
        search_result = engine.search_by_criteria(start, end, criteria)
        
        # Convert to JSON format
        result = {
            'success': True,
            'search_parameters': {
                'range': {'start': start, 'end': end},
                'criteria': criteria
            },
            'results': {
                'total_found': search_result.total_found,
                'density_statistics': search_result.density_statistics,
                'anomaly_score': search_result.anomaly_score,
                'points': [geodesic_point_to_dict(p) for p in search_result.points]
            }
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/clusters', methods=['POST'])
@rate_limit(max_requests_per_minute=15)
def find_clusters():
    """
    Find prime clusters in geodesic space.
    
    Request body:
    {
        "start": 2,
        "end": 1000,
        "eps": 0.1,
        "min_samples": 3
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        start = data.get('start', 2)
        end = data.get('end', 100)
        eps = data.get('eps', 0.1)
        min_samples = data.get('min_samples', 3)
        
        validate_range(start, end, max_range=2000)
        
        # Generate coordinates
        points = engine.generate_sequence_coordinates(start, end)
        
        # Find clusters
        clusters = engine.search_prime_clusters(points, eps=eps, min_samples=min_samples)
        
        # Format results
        cluster_data = []
        for i, cluster in enumerate(clusters):
            cluster_info = {
                'cluster_id': i,
                'size': len(cluster),
                'centroid': {
                    'x': np.mean([p.coordinates_3d[0] for p in cluster]),
                    'y': np.mean([p.coordinates_3d[1] for p in cluster]),
                    'z': np.mean([p.coordinates_3d[2] for p in cluster])
                },
                'primes': [p.n for p in cluster],
                'average_curvature': np.mean([p.curvature for p in cluster]),
                'density_enhancement_range': {
                    'min': min(p.density_enhancement for p in cluster),
                    'max': max(p.density_enhancement for p in cluster)
                },
                'points': [geodesic_point_to_dict(p) for p in cluster]
            }
            cluster_data.append(cluster_info)
        
        result = {
            'success': True,
            'parameters': {
                'range': {'start': start, 'end': end},
                'clustering': {'eps': eps, 'min_samples': min_samples}
            },
            'results': {
                'total_clusters': len(clusters),
                'total_clustered_primes': sum(len(cluster) for cluster in clusters),
                'clustering_efficiency': sum(len(cluster) for cluster in clusters) / len([p for p in points if p.is_prime]) if points else 0,
                'clusters': cluster_data
            }
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/anomalies', methods=['POST'])
@rate_limit(max_requests_per_minute=15)
def detect_anomalies():
    """
    Detect gaps and anomalies in geodesic sequences.
    
    Request body:
    {
        "start": 2,
        "end": 1000,
        "gap_threshold": 2.0,
        "curvature_anomaly_ratio": 3.0
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        start = data.get('start', 2)
        end = data.get('end', 100)
        gap_threshold = data.get('gap_threshold', 2.0)
        
        validate_range(start, end, max_range=5000)
        
        # Generate coordinates
        points = engine.generate_sequence_coordinates(start, end)
        
        # Find anomalies
        anomaly_results = engine.search_gaps_and_anomalies(points, gap_threshold=gap_threshold)
        
        result = {
            'success': True,
            'parameters': {
                'range': {'start': start, 'end': end},
                'gap_threshold': gap_threshold
            },
            'results': {
                'gaps': anomaly_results['gaps'],
                'anomalies': anomaly_results['anomalies'],
                'summary': {
                    'total_gaps': len(anomaly_results['gaps']),
                    'total_anomalies': len(anomaly_results['anomalies']),
                    'largest_gap': max(gap['distance'] for gap in anomaly_results['gaps']) if anomaly_results['gaps'] else 0,
                    'anomaly_types': list(set(anom['type'] for anom in anomaly_results['anomalies']))
                }
            }
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/statistics', methods=['POST'])
@rate_limit(max_requests_per_minute=10)
def generate_statistics():
    """
    Generate comprehensive statistical analysis.
    
    Request body:
    {
        "start": 2,
        "end": 1000,
        "include_validation": true
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        start = data.get('start', 2)
        end = data.get('end', 100)
        include_validation = data.get('include_validation', True)
        
        validate_range(start, end, max_range=10000)
        
        # Generate coordinates
        points = engine.generate_sequence_coordinates(start, end)
        
        # Generate statistical report
        report = engine.generate_statistical_report(points)
        
        # Add API-specific metadata
        result = {
            'success': True,
            'parameters': {
                'range': {'start': start, 'end': end},
                'k_optimal': engine.k_optimal
            },
            'statistics': report,
            'computation_metadata': {
                'timestamp': time.time(),
                'total_points_analyzed': len(points),
                'computation_engine': 'Z Framework Discrete Domain'
            }
        }
        
        if include_validation:
            # Add validation against empirical benchmarks
            primes = [p for p in points if p.is_prime]
            validation = {
                'empirical_benchmarks': {
                    'expected_enhancement': 15.0,  # From CI [14.6%, 15.4%]
                    'expected_variance': 0.118,
                    'optimal_k': 0.3
                },
                'achieved_metrics': {
                    'enhancement': np.mean([p.density_enhancement for p in primes]) if primes else 0,
                    'variance': np.var([p.curvature for p in points]) if points else 0,
                    'k_used': engine.k_optimal
                },
                'validation_status': {
                    'enhancement_valid': abs(np.mean([p.density_enhancement for p in primes]) - 15.0) < 2.0 if primes else False,
                    'variance_valid': abs(np.var([p.curvature for p in points]) - 0.118) < 0.05 if points else False,
                    'k_optimal': engine.k_optimal == 0.3
                }
            }
            result['validation'] = validation
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/validate', methods=['POST'])
@rate_limit(max_requests_per_minute=5)
def validate_framework():
    """
    Validate Z Framework predictions against known benchmarks.
    
    Request body:
    {
        "test_ranges": [
            {"start": 2, "end": 100},
            {"start": 100, "end": 1000}
        ],
        "validation_type": "density_enhancement"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        test_ranges = data.get('test_ranges', [{'start': 2, 'end': 100}])
        validation_type = data.get('validation_type', 'density_enhancement')
        
        validation_results = []
        
        for test_range in test_ranges:
            start = test_range.get('start', 2)
            end = test_range.get('end', 100)
            
            validate_range(start, end, max_range=2000)
            
            # Generate coordinates for this range
            points = engine.generate_sequence_coordinates(start, end)
            primes = [p for p in points if p.is_prime]
            
            if validation_type == 'density_enhancement':
                achieved_enhancement = np.mean([p.density_enhancement for p in primes]) if primes else 0
                expected_enhancement = 15.0
                validation_passed = abs(achieved_enhancement - expected_enhancement) < 3.0
                
                range_result = {
                    'range': {'start': start, 'end': end},
                    'metric': 'density_enhancement',
                    'expected': expected_enhancement,
                    'achieved': achieved_enhancement,
                    'deviation': abs(achieved_enhancement - expected_enhancement),
                    'validation_passed': validation_passed,
                    'prime_count': len(primes),
                    'total_points': len(points)
                }
            
            elif validation_type == 'curvature_variance':
                achieved_variance = np.var([p.curvature for p in points]) if points else 0
                expected_variance = 0.118
                validation_passed = abs(achieved_variance - expected_variance) < 0.05
                
                range_result = {
                    'range': {'start': start, 'end': end},
                    'metric': 'curvature_variance',
                    'expected': expected_variance,
                    'achieved': achieved_variance,
                    'deviation': abs(achieved_variance - expected_variance),
                    'validation_passed': validation_passed,
                    'sample_size': len(points)
                }
            
            else:
                return jsonify({'error': f'Unknown validation type: {validation_type}'}), 400
            
            validation_results.append(range_result)
        
        # Overall validation summary
        overall_passed = all(result['validation_passed'] for result in validation_results)
        
        result = {
            'success': True,
            'validation_type': validation_type,
            'overall_validation_passed': overall_passed,
            'test_ranges_count': len(test_ranges),
            'framework_parameters': {
                'k_optimal': engine.k_optimal,
                'phi': engine.phi
            },
            'results': validation_results,
            'summary': {
                'passed_tests': sum(1 for r in validation_results if r['validation_passed']),
                'total_tests': len(validation_results),
                'success_rate': sum(1 for r in validation_results if r['validation_passed']) / len(validation_results) if validation_results else 0
            }
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/batch', methods=['POST'])
@rate_limit(max_requests_per_minute=2)
def batch_process():
    """
    Batch processing for large datasets.
    
    Request body:
    {
        "sequences": [
            {"start": 2, "end": 1000, "id": "test1"},
            {"start": 1000, "end": 2000, "id": "test2"}
        ],
        "operations": ["coordinates", "clusters", "statistics"],
        "output_format": "json"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        sequences = data.get('sequences', [])
        operations = data.get('operations', ['coordinates'])
        output_format = data.get('output_format', 'json')
        
        if len(sequences) > 10:
            return jsonify({'error': 'Maximum 10 sequences per batch request'}), 400
        
        batch_results = []
        
        for seq_config in sequences:
            start = seq_config.get('start', 2)
            end = seq_config.get('end', 100)
            seq_id = seq_config.get('id', f'seq_{start}_{end}')
            
            validate_range(start, end, max_range=5000)
            
            # Generate coordinates
            points = engine.generate_sequence_coordinates(start, end)
            
            seq_result = {
                'sequence_id': seq_id,
                'range': {'start': start, 'end': end},
                'total_points': len(points)
            }
            
            # Perform requested operations
            if 'coordinates' in operations:
                seq_result['coordinates'] = [geodesic_point_to_dict(p) for p in points]
            
            if 'clusters' in operations:
                clusters = engine.search_prime_clusters(points, eps=0.2, min_samples=3)
                seq_result['clusters'] = {
                    'count': len(clusters),
                    'data': [
                        {
                            'cluster_id': i,
                            'primes': [p.n for p in cluster],
                            'size': len(cluster)
                        }
                        for i, cluster in enumerate(clusters)
                    ]
                }
            
            if 'statistics' in operations:
                stats = engine.generate_statistical_report(points)
                seq_result['statistics'] = stats
            
            if 'anomalies' in operations:
                anomalies = engine.search_gaps_and_anomalies(points)
                seq_result['anomalies'] = {
                    'gaps_count': len(anomalies['gaps']),
                    'anomalies_count': len(anomalies['anomalies']),
                    'details': anomalies
                }
            
            batch_results.append(seq_result)
        
        result = {
            'success': True,
            'batch_id': hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            'operations_performed': operations,
            'sequences_processed': len(sequences),
            'output_format': output_format,
            'results': batch_results,
            'processing_metadata': {
                'timestamp': time.time(),
                'total_points_computed': sum(r['total_points'] for r in batch_results),
                'framework_version': '1.0.0'
            }
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'engine_status': 'operational',
        'cache_size': len(request_cache),
        'framework_parameters': {
            'k_optimal': engine.k_optimal,
            'phi': engine.phi
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Prime Geodesic API Server...")
    print("API Documentation available at: http://localhost:5001/api/v1")
    print("Health check: http://localhost:5001/api/v1/health")
    app.run(debug=True, host='0.0.0.0', port=5001)