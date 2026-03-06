"""
Universal Invariant Scoring Engine REST API Server

Provides HTTP endpoints for Z-invariant scoring and density analysis.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from typing import Any, Dict, List, Optional
import traceback

from .scoring_engine import create_scoring_engine, UniversalScoringEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-domain requests

# Global scoring engine instance
scoring_engine: Optional[UniversalScoringEngine] = None


def get_scoring_engine() -> UniversalScoringEngine:
    """Get or create scoring engine instance."""
    global scoring_engine
    if scoring_engine is None:
        scoring_engine = create_scoring_engine()
    return scoring_engine


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Universal Invariant Scoring Engine',
        'version': '1.0.0'
    })


@app.route('/api/score', methods=['POST'])
def score_sequence():
    """
    Score a single sequence.
    
    Expected JSON payload:
    {
        "data": [1, 2, 3, 4, 5],  # or "ATGC" for biological, or matrix for network
        "data_type": "numerical"   # optional: "numerical", "biological", "network", "auto"
    }
    """
    try:
        # Parse request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        payload = request.get_json()
        if not payload or 'data' not in payload:
            return jsonify({'error': 'Missing required field: data'}), 400
        
        data = payload['data']
        data_type = payload.get('data_type', 'auto')
        
        # Score the sequence
        engine = get_scoring_engine()
        result = engine.score_sequence(data, data_type)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error in score_sequence: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500


@app.route('/api/batch_score', methods=['POST'])
def batch_score():
    """
    Score multiple sequences in batch.
    
    Expected JSON payload:
    {
        "data_list": [
            [1, 2, 3, 4, 5],
            "ATGCATGC",
            [[0, 1], [1, 0]]
        ],
        "data_types": ["numerical", "biological", "network"]  # optional
    }
    """
    try:
        # Parse request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        payload = request.get_json()
        if not payload or 'data_list' not in payload:
            return jsonify({'error': 'Missing required field: data_list'}), 400
        
        data_list = payload['data_list']
        data_types = payload.get('data_types', None)
        
        if not isinstance(data_list, list):
            return jsonify({'error': 'data_list must be an array'}), 400
        
        # Score the sequences
        engine = get_scoring_engine()
        results = engine.batch_score(data_list, data_types)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_processed': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in batch_score: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_sequence():
    """
    Comprehensive analysis of a sequence with detailed breakdown.
    
    Expected JSON payload:
    {
        "data": [1, 2, 3, 4, 5],
        "data_type": "numerical",
        "include_normalized": true,    # optional: include normalized sequence in response
        "detailed_metrics": true       # optional: include detailed sub-metrics
    }
    """
    try:
        # Parse request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        payload = request.get_json()
        if not payload or 'data' not in payload:
            return jsonify({'error': 'Missing required field: data'}), 400
        
        data = payload['data']
        data_type = payload.get('data_type', 'auto')
        include_normalized = payload.get('include_normalized', False)
        detailed_metrics = payload.get('detailed_metrics', False)
        
        # Score the sequence
        engine = get_scoring_engine()
        result = engine.score_sequence(data, data_type)
        
        # Enhance response based on options
        analysis_result = {
            'metadata': result['metadata'],
            'summary': {
                'z_invariant_score': result['z_invariant_score'],
                'composite_anomaly_score': result['anomaly_scores']['composite_anomaly_score'],
                'enhancement_factor': result['density_metrics']['enhancement_factor'],
                'sequence_length': result['sequence_length']
            }
        }
        
        if detailed_metrics:
            analysis_result.update({
                'z_scores': result['z_scores'],
                'density_metrics': result['density_metrics'],
                'anomaly_scores': result['anomaly_scores']
            })
        
        if include_normalized:
            analysis_result['normalized_sequence'] = result['normalized_sequence']
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_sequence: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500


@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and supported data types."""
    return jsonify({
        'service': 'Universal Invariant Scoring Engine',
        'version': '1.0.0',
        'description': 'Z-invariant based scoring and density analysis for arbitrary sequences',
        'supported_data_types': [
            {
                'type': 'numerical',
                'description': 'Numerical sequences and arrays',
                'example': [1, 2, 3, 4, 5]
            },
            {
                'type': 'biological',
                'description': 'DNA, RNA, and protein sequences',
                'example': 'ATGCATGC'
            },
            {
                'type': 'network',
                'description': 'Network adjacency matrices',
                'example': [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
            }
        ],
        'endpoints': [
            {
                'path': '/api/score',
                'method': 'POST',
                'description': 'Score a single sequence'
            },
            {
                'path': '/api/batch_score',
                'method': 'POST',
                'description': 'Score multiple sequences in batch'
            },
            {
                'path': '/api/analyze',
                'method': 'POST',
                'description': 'Comprehensive sequence analysis'
            },
            {
                'path': '/api/info',
                'method': 'GET',
                'description': 'API information and documentation'
            }
        ]
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': ['/health', '/api/score', '/api/batch_score', '/api/analyze', '/api/info']
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please check the server logs.'
    }), 500


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask application
    """
    if config:
        app.config.update(config)
    
    return app


def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the Flask development server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    logger.info(f"Starting Universal Invariant Scoring Engine API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server(debug=True)