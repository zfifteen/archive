#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Run the experiment with default settings
# Default ranges are 1e6:1e7,1e7:1e8 which is small enough for a quick test
python run_experiment.py
