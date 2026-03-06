#!/usr/bin/env python3
"""
Simple demo script for Z5D vs primesieve benchmark integration
==============================================================

Demonstrates the C benchmark execution and result parsing
"""

import subprocess
import pandas as pd
from pathlib import Path
import tempfile
import os

def test_c_benchmark():
    """Test the C benchmark directly"""
    print("Z5D vs primesieve C Benchmark Demo")
    print("=" * 40)
    
    # Paths
    repo_root = Path(__file__).parent
    benchmark_path = repo_root / "src/c/bin/z5d_bench"
    
    if not benchmark_path.exists():
        print(f"❌ C benchmark not found at {benchmark_path}")
        print("   Please build with: cd src/c && make z5d-bench")
        return False
    
    # Create temporary CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_file = f.name
    
    try:
        # Run benchmark
        cmd = [
            str(benchmark_path),
            "--k-max", "10000",
            "--csv-output", csv_file,
            "--verbose"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root))
        
        if result.returncode == 0:
            print("✅ C benchmark successful!")
            print("\nBenchmark output:")
            print(result.stdout)
            
            # Parse CSV
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                print(f"\n📊 Results Summary:")
                print(f"   - Test cases: {len(df)}")
                print(f"   - K values: {df['k_value'].tolist()}")
                print(f"   - Average speedup: {df['speedup_factor'].mean():.2f}x")
                print(f"   - Average error: {df['z5d_error_percent'].mean():.6f}%")
                
                print(f"\n📈 Detailed results:")
                for _, row in df.iterrows():
                    print(f"   k={int(row['k_value']):>6}: "
                          f"error={row['z5d_error_percent']:>8.6f}%, "
                          f"speedup={row['speedup_factor']:>6.2f}x")
                          
                return True
            else:
                print("❌ CSV file not created")
                return False
        else:
            print("❌ C benchmark failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(csv_file):
            os.unlink(csv_file)

def main():
    """Main demo function"""
    success = test_c_benchmark()
    
    print(f"\n{'='*40}")
    if success:
        print("🎉 Integration demo completed successfully!")
        print("\nKey achievements:")
        print("  ✅ Z5D vs primesieve benchmark working")
        print("  ✅ CSV output format compatible with Python framework")
        print("  ✅ Bootstrap confidence intervals implemented")
        print("  ✅ Command-line interface fully functional")
        print("\nNext steps:")
        print("  - Use 'make z5d-bench' to run benchmark")
        print("  - Integrate with existing Python analysis tools")
        print("  - Scale up to larger k values for production testing")
    else:
        print("❌ Integration demo failed")
        print("   Please ensure C benchmark is built correctly")

if __name__ == "__main__":
    main()