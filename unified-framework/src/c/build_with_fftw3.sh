#!/bin/bash

# Script to build z5d_prime_gen with FFTW3 enabled
# Ensures a clean build and sets necessary flags for FFT-zeta enhancement

echo "Starting build process for z5d_prime_gen with FFTW3 enabled..."

# Clean previous build artifacts
make clean

# Build with FFT-zeta enhancement enabled
echo "Building z5d_prime_gen with FFT_ZETA_ENHANCE=1 and FFTW_AVAILABLE=1..."
make gen FFT_ZETA_ENHANCE=1 FFTW_AVAILABLE=1

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful! Testing the binary..."
    # Run a test with the built binary to confirm FFT enablement
    ./bin/z5d_prime_gen 1000
else
    echo "Build failed. Please check the output for errors."
    exit 1
fi

echo "Build and test process complete."
