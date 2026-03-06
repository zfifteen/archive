#!/usr/bin/env python3
"""
Setup Script for Zeta Zeros Dataset

This script sets up the zeta zeros dataset for the unified framework.
It converts existing data to numpy format and validates the dataset.

Run this script to generate src/data/zeta_zeros.npy from existing data.
"""

import os
import subprocess
import sys

def main():
    """Setup the zeta zeros dataset."""
    print("Setting up Zeta Zeros Dataset for Unified Framework")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('scripts') or not os.path.exists('data'):
        print("❌ Please run this script from the repository root directory")
        return False
    
    # Check if conversion script exists
    convert_script = os.path.join('scripts', 'convert_zeta_to_numpy.py')
    if not os.path.exists(convert_script):
        print(f"❌ Conversion script not found: {convert_script}")
        return False
    
    # Check if source data exists
    source_data = os.path.join('data', 'zeta_1M.txt')
    if not os.path.exists(source_data):
        print(f"❌ Source data not found: {source_data}")
        print("   Please ensure the repository includes the zeta_1M.txt file")
        return False
    
    print("✓ Found required files")
    print(f"  Source data: {source_data}")
    print(f"  Conversion script: {convert_script}")
    print()
    
    # Run conversion
    print("Converting zeta zeros to numpy format...")
    try:
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
        
        result = subprocess.run([
            sys.executable, os.path.abspath(convert_script)
        ], cwd=os.path.dirname(convert_script), capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✓ Conversion completed successfully")
            if result.stdout:
                print("Conversion output:")
                print(result.stdout)
        else:
            print("❌ Conversion failed")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running conversion: {e}")
        return False
    
    # Verify the output
    output_file = os.path.join('src', 'data', 'zeta_zeros.npy')
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✓ Dataset created: {output_file}")
        print(f"  File size: {file_size:,} bytes ({file_size/(1024**2):.1f} MB)")
        
        # Quick validation
        try:
            import numpy as np
            zeros = np.load(output_file)
            print(f"  Zeros count: {len(zeros):,}")
            print(f"  Data type: {zeros.dtype}")
            print(f"  First zero: {zeros[0]}")
            print("✓ Dataset validation passed")
            
        except Exception as e:
            print(f"⚠️  Dataset validation failed: {e}")
            return False
    else:
        print(f"❌ Dataset file not created: {output_file}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ZETA ZEROS DATASET SETUP COMPLETE")
    print()
    print("Next steps:")
    print("  1. Run tests: python scripts/test_vectorized_zeta_zeros.py")
    print("  2. Full validation: python scripts/test_full_million_zeros.py") 
    print("  3. Integration test: python scripts/test_integration.py")
    print()
    print("The dataset is now ready for use in research and benchmarks.")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)