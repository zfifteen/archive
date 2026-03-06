#!/usr/bin/env python3
"""
Download Odlyzko/LMFDB Zeta Zeros Dataset

This script downloads the first 10^6 nontrivial zeros of the Riemann zeta function
from the Odlyzko/LMFDB database and converts them to numpy format for use in
the unified framework.

Sources:
- LMFDB: L-functions and Modular Forms Database (https://www.lmfdb.org/)
- Odlyzko's zeros: High-precision computation of Riemann zeta zeros
- Public domain mathematical data

The zeros are saved in numpy format as src/data/zeta_zeros.npy for efficient
vectorized operations in benchmarks and analysis.
"""

import os
import sys
import numpy as np
import requests
import gzip
import time
from urllib.parse import urljoin
from typing import List, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def download_file_with_progress(url: str, output_path: str, chunk_size: int = 8192) -> bool:
    """
    Download a file with progress indication.
    
    Args:
        url: URL to download from
        output_path: Local path to save file
        chunk_size: Size of chunks to download
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Downloading from: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgress: {progress:.1f}% ({downloaded:,} / {total_size:,} bytes)", end='')
                    else:
                        print(f"\rDownloaded: {downloaded:,} bytes", end='')
        
        print()  # New line after progress
        return True
        
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def fetch_lmfdb_zeros_list() -> List[str]:
    """
    Get available zeta zeros datasets from LMFDB.
    
    Returns:
        List of available dataset URLs/identifiers
    """
    # Note: LMFDB API structure for zeta zeros
    # This is a simplified approach - in practice, you might need to scrape or use specific APIs
    
    # Known sources for Riemann zeta zeros
    known_sources = [
        # LMFDB zeros (if available via direct download)
        "https://www.lmfdb.org/download/zeros/zeta/",
        # Alternative: use existing data and augment with computed zeros
        "local_computation"  # Fallback to local computation
    ]
    
    return known_sources

def parse_odlyzko_format(text_data: str) -> List[complex]:
    """
    Parse zeta zeros from Odlyzko-style text format.
    
    Expected format variations:
    - "14.134725142" (just imaginary part)
    - "0.5 14.134725142" (real and imaginary)
    - "1 14.134725142" (index and imaginary)
    
    Args:
        text_data: Raw text data containing zeros
        
    Returns:
        List of complex zeros (all with real part 0.5)
    """
    zeros = []
    lines = text_data.strip().split('\n')
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        try:
            parts = line.split()
            
            if len(parts) == 1:
                # Just imaginary part
                imag = float(parts[0])
                zeros.append(complex(0.5, imag))
            elif len(parts) == 2:
                # Could be "real imag" or "index imag"
                try:
                    val1, val2 = float(parts[0]), float(parts[1])
                    if abs(val1 - 0.5) < 0.01:  # Likely real part
                        zeros.append(complex(val1, val2))
                    else:  # Likely index, val2 is imaginary part
                        zeros.append(complex(0.5, val2))
                except ValueError:
                    continue
            else:
                # Try to extract the last numeric value as imaginary part
                try:
                    imag = float(parts[-1])
                    zeros.append(complex(0.5, imag))
                except ValueError:
                    continue
                    
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse line {line_num + 1}: '{line}' ({e})")
            continue
    
    return zeros

def compute_high_precision_zeros(max_zeros: int = 1000000) -> List[complex]:
    """
    Compute zeta zeros using high-precision methods when download fails.
    
    This is a fallback method that uses existing computational methods
    to generate zeros if external datasets are not available.
    
    Args:
        max_zeros: Maximum number of zeros to compute
        
    Returns:
        List of computed complex zeros
    """
    print(f"Computing {max_zeros} zeta zeros using high-precision methods...")
    
    # Try to use existing zeta processing infrastructure
    try:
        from statistical.zeta_zeros_extended import ExtendedZetaZeroProcessor
        
        processor = ExtendedZetaZeroProcessor(precision_dps=50)
        
        # Compute in batches to manage memory
        batch_size = min(1000, max_zeros)
        all_zeros = []
        
        for start_idx in range(1, max_zeros + 1, batch_size):
            end_idx = min(start_idx + batch_size - 1, max_zeros)
            print(f"Computing zeros {start_idx} to {end_idx}...")
            
            batch_data = processor.compute_zeta_zeros_batch(
                j_start=start_idx, 
                j_end=end_idx, 
                batch_size=batch_size
            )
            
            if batch_data and 'zeros' in batch_data:
                all_zeros.extend(batch_data['zeros'])
            
            # Rate limiting to prevent overload
            if end_idx < max_zeros:
                time.sleep(0.1)
        
        return all_zeros[:max_zeros]  # Ensure we don't exceed requested count
        
    except ImportError as e:
        print(f"Could not import zeta processing infrastructure: {e}")
        return []
    except Exception as e:
        print(f"Error in high-precision computation: {e}")
        return []

def download_odlyzko_lmfdb_zeros(max_zeros: int = 1000000) -> Optional[List[complex]]:
    """
    Download Odlyzko/LMFDB zeta zeros dataset.
    
    Args:
        max_zeros: Maximum number of zeros to download
        
    Returns:
        List of complex zeros or None if download fails
    """
    print("=" * 80)
    print("DOWNLOADING ODLYZKO/LMFDB ZETA ZEROS DATASET")
    print("=" * 80)
    print(f"Target: First {max_zeros:,} nontrivial zeros of Riemann zeta function")
    print("Sources: LMFDB, Odlyzko's high-precision computations")
    print()
    
    # Try multiple download strategies
    download_strategies = [
        ("existing_file", "Use existing zeta_1M.txt if sufficient"),
        ("lmfdb_api", "Download from LMFDB database"),
        ("odlyzko_mirror", "Download from Odlyzko data mirrors"),
        ("local_computation", "Compute using high-precision methods")
    ]
    
    for strategy_name, strategy_desc in download_strategies:
        print(f"Trying strategy: {strategy_name} - {strategy_desc}")
        
        if strategy_name == "existing_file":
            # Check if we already have sufficient data
            existing_file = os.path.join('..', 'data', 'zeta_1M.txt')
            if os.path.exists(existing_file):
                print(f"Found existing file: {existing_file}")
                try:
                    with open(existing_file, 'r') as f:
                        content = f.read()
                    
                    zeros = parse_odlyzko_format(content)
                    if len(zeros) >= max_zeros:
                        print(f"✓ Using existing data: {len(zeros)} zeros available")
                        return zeros[:max_zeros]
                    else:
                        print(f"Existing data insufficient: {len(zeros)} < {max_zeros}")
                        continue
                        
                except Exception as e:
                    print(f"Error reading existing file: {e}")
                    continue
            else:
                print("No existing file found")
                continue
        
        elif strategy_name == "lmfdb_api":
            # Try LMFDB API or download URLs
            lmfdb_urls = [
                "https://www.lmfdb.org/download/zeta/zeros.txt.gz",
                "https://www.lmfdb.org/api/zeta_zeros",
                "https://www.lmfdb.org/zeros/zeta/download"
            ]
            
            for url in lmfdb_urls:
                print(f"  Attempting: {url}")
                try:
                    temp_file = "/tmp/lmfdb_zeros.txt"
                    if download_file_with_progress(url, temp_file):
                        with open(temp_file, 'r') as f:
                            content = f.read()
                        
                        zeros = parse_odlyzko_format(content)
                        if len(zeros) >= max_zeros:
                            print(f"✓ Downloaded {len(zeros)} zeros from LMFDB")
                            return zeros[:max_zeros]
                        else:
                            print(f"Downloaded data insufficient: {len(zeros)} zeros")
                
                except Exception as e:
                    print(f"  Failed: {e}")
                    continue
        
        elif strategy_name == "odlyzko_mirror":
            # Try known Odlyzko data mirrors
            odlyzko_urls = [
                "http://www.dtc.umn.edu/~odlyzko/zeta_tables/zeros1",
                "https://faculty.math.illinois.edu/~hiary/zeros.txt",
                "https://oeis.org/A002410/b002410.txt"  # OEIS sequence for zeta zeros
            ]
            
            for url in odlyzko_urls:
                print(f"  Attempting: {url}")
                try:
                    temp_file = "/tmp/odlyzko_zeros.txt"
                    if download_file_with_progress(url, temp_file):
                        with open(temp_file, 'r') as f:
                            content = f.read()
                        
                        zeros = parse_odlyzko_format(content)
                        if len(zeros) >= max_zeros:
                            print(f"✓ Downloaded {len(zeros)} zeros from Odlyzko mirror")
                            return zeros[:max_zeros]
                        else:
                            print(f"Downloaded data insufficient: {len(zeros)} zeros")
                
                except Exception as e:
                    print(f"  Failed: {e}")
                    continue
        
        elif strategy_name == "local_computation":
            # Fallback to local computation
            print("  Computing zeros using local high-precision methods...")
            zeros = compute_high_precision_zeros(max_zeros)
            if len(zeros) >= max_zeros:
                print(f"✓ Computed {len(zeros)} zeros locally")
                return zeros[:max_zeros]
            else:
                print(f"Local computation insufficient: {len(zeros)} zeros")
        
        print(f"Strategy '{strategy_name}' failed or insufficient")
        print()
    
    print("❌ All download strategies failed")
    return None

def save_zeros_to_numpy(zeros: List[complex], output_path: str) -> bool:
    """
    Save zeta zeros to numpy format.
    
    Args:
        zeros: List of complex zeros
        output_path: Path to save numpy file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert to numpy array
        zeros_array = np.array(zeros, dtype=complex)
        
        # Save in numpy format
        np.save(output_path, zeros_array)
        
        print(f"✓ Saved {len(zeros)} zeros to {output_path}")
        print(f"  File size: {os.path.getsize(output_path):,} bytes")
        print(f"  Data type: {zeros_array.dtype}")
        print(f"  Array shape: {zeros_array.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving zeros to numpy: {e}")
        return False

def validate_zeros_data(zeros: List[complex], max_zeros: int) -> bool:
    """
    Validate the downloaded/computed zeros data.
    
    Args:
        zeros: List of zeros to validate
        max_zeros: Expected maximum number of zeros
        
    Returns:
        True if validation passes, False otherwise
    """
    print("\nValidating zeros data...")
    
    if not zeros:
        print("❌ No zeros data to validate")
        return False
    
    if len(zeros) < max_zeros:
        print(f"⚠️  Warning: Expected {max_zeros} zeros, got {len(zeros)}")
    
    # Check that all zeros have real part ≈ 0.5
    real_parts = [z.real for z in zeros[:100]]  # Check first 100
    avg_real = np.mean(real_parts)
    
    if abs(avg_real - 0.5) > 0.01:
        print(f"❌ Invalid real parts: average = {avg_real}, expected ≈ 0.5")
        return False
    
    # Check that imaginary parts are positive and increasing
    imag_parts = [z.imag for z in zeros[:100]]
    if not all(im > 0 for im in imag_parts):
        print("❌ Found non-positive imaginary parts")
        return False
    
    if not all(imag_parts[i] < imag_parts[i+1] for i in range(len(imag_parts)-1)):
        print("❌ Imaginary parts are not in increasing order")
        return False
    
    # Check known first few zeros and assert no random variation/noise
    known_first_zeros = [
        14.134725142,   # First zero
        21.022039639,   # Second zero  
        25.010857580,   # Third zero
    ]
    
    if len(zeros) >= 3:
        actual_values = [zeros[i].imag for i in range(3)]
        expected_values = known_first_zeros
        
        # Calculate standard deviation of differences to detect noise
        differences = np.array(actual_values) - np.array(expected_values)
        noise_std = np.std(differences)
        
        print(f"  Noise validation: std(actual - expected) = {noise_std:.2e}")
        
        # Assert no significant random variation/noise (tolerance: 1e-6)
        assert noise_std < 1e-6, f"Random variation detected: std = {noise_std:.2e} > 1e-6"
        
        for i, expected_imag in enumerate(known_first_zeros):
            actual_imag = zeros[i].imag
            if abs(actual_imag - expected_imag) > 0.01:
                print(f"❌ Zero {i+1}: expected {expected_imag}, got {actual_imag}")
                return False
    
    print(f"✓ Validation passed for {len(zeros)} zeros")
    print(f"  Real parts average: {avg_real:.6f}")
    print(f"  First zero: {zeros[0]}")
    print(f"  Last zero: {zeros[-1]}")
    print(f"  ✓ No random variation/noise detected in critical zeros")
    
    return True

def main():
    """Main function to download and process Odlyzko/LMFDB zeta zeros."""
    print("Odlyzko/LMFDB Zeta Zeros Dataset Downloader")
    print("=" * 60)
    
    # Configuration
    max_zeros = 1000000  # First 10^6 zeros as requested
    output_path = os.path.join('..', 'src', 'data', 'zeta_zeros.npy')
    
    print(f"Target zeros: {max_zeros:,}")
    print(f"Output file: {output_path}")
    print()
    
    # Download zeros
    zeros = download_odlyzko_lmfdb_zeros(max_zeros)
    
    if zeros is None:
        print("❌ Failed to download/compute zeta zeros")
        return False
    
    # Validate data
    if not validate_zeros_data(zeros, max_zeros):
        print("❌ Data validation failed")
        return False
    
    # Save to numpy format
    if not save_zeros_to_numpy(zeros, output_path):
        print("❌ Failed to save zeros data")
        return False
    
    print("\n" + "=" * 60)
    print("✓ SUCCESS: Odlyzko/LMFDB zeta zeros dataset ready")
    print(f"  Location: {output_path}")
    print(f"  Zeros count: {len(zeros):,}")
    print(f"  Format: NumPy complex array")
    print("  Ready for vectorized benchmarks and analysis")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)