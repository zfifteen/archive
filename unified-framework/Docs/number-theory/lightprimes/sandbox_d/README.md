### Instructions

1. **Database and Embedding**:
   - `HarnessDatabase` for loading initial prime data
   - `StreamingDatabase` for managing the sliding window of primes
   - `embed_z` function for generating embeddings (dummy implementation)

2. **Prime Verification**:
   - Miller-Rabin primality test implementation

3. **Geometric Prediction**:
   - `GeometricPredictor` neural network for prime location prediction
   - `compute_theta` for adaptive threshold calculation
   - `inverse_embedding` for converting vectors back to integers

4. **Confidence Tracking**:
   - `PredictionTracker` for managing prediction accuracy history
   - `confidence_function` for calculating confidence scores

5. **Main Workflow**:
   - Phased operation between geometric filtering and predictive verification
   - Twin prime detection and tracking
   - Confidence-based mode transitions
   - Performance summary and sanity checks

Key features:
- Self-contained implementation (no external dependencies beyond standard libraries)
- All components integrated into a single file
- Fixed all syntax errors and undefined variables
- Added proper twin prime handling in both modes
- Implemented robust mode transitions with fallback mechanisms
- Included comprehensive performance summary

To run the script:
```bash
python prime_geometer.py --coords output_coords.npy --primes output_primes.txt --prime-count 6000
```

For twin prime mode:
```bash
python prime_geometer.py --coords output_coords.npy --primes output_primes.txt --prime-count 6000 --twin-mode
```

For predictive focusing:
```bash
python prime_geometer.py --coords output_coords.npy --primes output_primes.txt --prime-count 6000 --forecast
```