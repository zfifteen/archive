# Prime Grid Plot - C Implementation

A C implementation of `gists/prime_grid_plot.py` using GMP for arbitrary precision integer arithmetic. This tool generates grids of points (x, y) where N = x * 10^m + y is prime, supporting arbitrary scales through GMP's exact integer arithmetic.

## Features

- **GMP-based arbitrary precision integers**: Handles scales up to 10^1000+ using GMP library's exact integer arithmetic
- **Miller-Rabin primality testing**: Uses GMP's `mpz_probab_prime_p` with configurable rounds for proper primality testing
- **Flexible grid generation**: Support for both stepped iteration and random probing
- **CSV output**: Generates CSV files with x, y, N, and primality results
- **Command-line interface**: Matches Python version functionality
- **Reproducible results**: Optional seeded random number generation for probing

## Dependencies

- **GMP library**: GNU Multiple Precision Arithmetic library for exact integer arithmetic
- **Standard C library**: getopt_long for command-line parsing (GNU extension)

### Installation (Ubuntu/Debian)
```bash
sudo apt-get install libgmp-dev
```

### Installation (macOS with Homebrew)
```bash
brew install gmp
```

## Building

```bash
make          # Build the executable
make test     # Build and run demonstration
make clean    # Clean build artifacts
make help     # Show help information
```

## Usage

### Basic Usage
```bash
./bin/prime_grid_plot --scale "10^6" --x-start 1 --x-end 5 --y-start 0 --y-end 1000 --out-csv output.csv
```

### Command Line Options

**Required arguments:**
- `--scale SCALE`: Scale like '10^6' or raw exponent '6'
- `--x-start NUM`: Start x (inclusive)
- `--x-end NUM`: End x (inclusive)  
- `--y-start NUM`: Start y (inclusive)
- `--y-end NUM`: End y (inclusive)

**Optional arguments:**
- `--y-step NUM`: Step for y traversal (default: 1, ignored if --probes > 0)
- `--probes NUM`: Random probes in [y-start, y-end] (default: 0 = disabled)
- `--mr-rounds NUM`: Miller-Rabin rounds for GMP primality test (default: 25)
- `--seed NUM`: Random seed for reproducible probes
- `--out-csv FILE`: Output CSV file path (stores x,y,N,is_prime)
- `--verbose`: Enable verbose output
- `--help`: Show help message

## Examples

### Dense Sampling at Moderate Scale
```bash
./bin/prime_grid_plot --scale "10^6" --x-start 1 --x-end 5 \
    --y-start 0 --y-end 20000 --y-step 1 \
    --out-csv grid_1e6.csv --verbose
```

### Random Probing at Large Scale
```bash
./bin/prime_grid_plot --scale "10^9" --x-start 1 --x-end 3 \
    --y-start 0 --y-end 1000000 --probes 20000 \
    --seed 42 --out-csv grid_1e9.csv --verbose
```

### Ultra-Large Scale (Demonstration)
```bash
./bin/prime_grid_plot --scale "10^1234" --x-start 1 --x-end 2 \
    --y-start 0 --y-end 1000000000000 --probes 5000 \
    --mr-rounds 24 --out-csv grid_1e1234.csv
```

## Output Format

The tool generates CSV files with the following columns:
- `x`: x coordinate
- `y`: y coordinate  
- `N`: The actual number N = x * 10^m + y (arbitrary precision)
- `is_prime`: 1 if N is probably prime, 0 if composite

## Demonstration

Run the included demonstration script:
```bash
./demo.sh
```

This will generate several example CSV files showing different scales and sampling methods.

## Implementation Notes

- **GMP Integer Arithmetic**: Uses exact arbitrary precision integer arithmetic for all N = x * 10^m + y calculations
- **Miller-Rabin Testing**: Uses GMP's `mpz_probab_prime_p` with trial divisions + Baillie-PSW + Miller-Rabin tests
- **Memory Management**: Efficient GMP memory management for large integer operations
- **Cross-Platform**: Works on Linux, macOS, and Windows (with MinGW/MSYS2)

## Differences from Python Version

- **No plotting**: The C version generates CSV data only (use external tools for visualization)
- **GMP integer arithmetic**: Uses GMP's exact integer arithmetic instead of Python's arbitrary precision integers
- **Proper Miller-Rabin**: Uses GMP's standard implementation with proper bases and deterministic small-prime tests
- **Performance**: Significantly faster for large-scale computations with better memory efficiency

## Visualization

To visualize the generated CSV data, use Python:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('output.csv')
primes = df[df['is_prime'] == 1]

plt.figure(figsize=(10, 6))
plt.scatter(primes['x'], primes['y'], s=6, alpha=0.7)
plt.title('Prime Grid Plot')
plt.xlabel('x')
plt.ylabel('y')
plt.show()
```

## License

This implementation follows the same license as the unified-framework project.