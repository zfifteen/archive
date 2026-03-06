"""
Run all tests for the lognormal prefilter factorization pipeline.
"""
import sys
import os

# Add tests directory to path
sys.path.insert(0, os.path.dirname(__file__))

from test_model import run_all_tests as run_model_tests
from test_sampling import run_all_tests as run_sampling_tests
from test_fermat import run_all_tests as run_fermat_tests
from test_prefilter import run_all_tests as run_prefilter_tests
from test_pipeline import run_all_tests as run_pipeline_tests


def main():
    """Run all test suites."""
    print("=" * 60)
    print("Running Lognormal Prefilter Factorization Tests")
    print("=" * 60)
    print()
    
    try:
        print("1. Model Tests")
        print("-" * 60)
        run_model_tests()
        print()
        
        print("2. Sampling Tests")
        print("-" * 60)
        run_sampling_tests()
        print()
        
        print("3. Fermat Tests")
        print("-" * 60)
        run_fermat_tests()
        print()
        
        print("4. Prefilter Tests")
        print("-" * 60)
        run_prefilter_tests()
        print()
        
        print("5. Pipeline Tests")
        print("-" * 60)
        run_pipeline_tests()
        print()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
