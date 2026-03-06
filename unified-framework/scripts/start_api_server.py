#!/usr/bin/env python3
"""
Universal Invariant Scoring Engine API Server

Start script for the Z-score API server.
"""

import os
import sys
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set PYTHONPATH for proper imports
os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))

from src.api.server import run_server


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Universal Invariant Scoring Engine API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Universal Invariant Scoring Engine API Server")
    print("Built on the Z Framework mathematical foundations")
    print("=" * 60)
    print(f"Starting server on {args.host}:{args.port}")
    print(f"Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    print("")
    print("API Endpoints:")
    print(f"  Health Check: http://{args.host}:{args.port}/health")
    print(f"  Score API:    http://{args.host}:{args.port}/api/score")
    print(f"  Batch Score:  http://{args.host}:{args.port}/api/batch_score")
    print(f"  Analyze:      http://{args.host}:{args.port}/api/analyze")
    print(f"  API Info:     http://{args.host}:{args.port}/api/info")
    print("")
    print("Documentation: docs/API_DOCUMENTATION.md")
    print("Demo Script:   python3 demo_api_scoring.py")
    print("=" * 60)
    
    try:
        run_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nServer shutdown requested by user")
    except Exception as e:
        print(f"\nServer error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()