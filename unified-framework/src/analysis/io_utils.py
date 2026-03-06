"""
IO Utilities for Z5D Riemann Scaling Anomaly Analysis
=====================================================

Robust parsing utilities for white paper data in multiple formats.
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from typing import Optional


def load_white_paper(path: str) -> pd.DataFrame:
    """
    Load white paper data with robust parsing for MD/CSV/TSV formats.
    
    Args:
        path: Path to white paper file
        
    Returns:
        pd.DataFrame with columns: k, p_true, p_hat_z5d, err_abs, err_rel, logk
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"White paper file not found: {path}")
    
    # Read file content
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to extract data from markdown format first
    df = _parse_markdown_data(content)
    
    if df is None:
        # Fall back to direct CSV/TSV parsing
        df = _parse_csv_data(path)
    
    if df is None:
        raise ValueError(f"Could not parse data from {path}. Expected CSV/TSV or markdown with data table.")
    
    # Validate required columns
    required_cols = ['k', 'p_true', 'p_hat_z5d']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Compute derived columns if not present
    if 'err_abs' not in df.columns:
        df['err_abs'] = df['p_true'] - df['p_hat_z5d']
    
    if 'err_rel' not in df.columns:
        df['err_rel'] = (df['p_true'] - df['p_hat_z5d']) / df['p_true']
    
    # Add log(k) for analysis
    df['logk'] = np.log(df['k'].astype(float))
    
    # Filter out k=1 since log(1)=0 makes 1/log²(1) undefined
    if 1 in df['k'].values:
        print("Warning: Filtering out k=1 since 1/log²(1) is undefined")
        df = df[df['k'] > 1].reset_index(drop=True)
    
    # Sort by k and reset index
    df = df.sort_values('k').reset_index(drop=True)
    
    # Validate data quality
    _validate_data_quality(df)
    
    return df


def _parse_markdown_data(content: str) -> Optional[pd.DataFrame]:
    """Extract data table from markdown content."""
    # Look for CSV-like data in code blocks or after headers
    lines = content.split('\n')
    
    # Find data section
    data_lines = []
    in_data_section = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and markdown formatting
        if not line or line.startswith('#') or line.startswith('```'):
            continue
            
        # Check if this looks like a CSV header or data line
        if ',' in line and ('k,' in line or line.replace(',', '').replace('.', '').replace('-', '').replace('e', '').isalnum()):
            data_lines.append(line)
            in_data_section = True
        elif in_data_section and not (',' in line):
            # End of data section
            break
    
    if not data_lines:
        return None
    
    # Parse CSV data
    try:
        from io import StringIO
        csv_content = '\n'.join(data_lines)
        df = pd.read_csv(StringIO(csv_content))
        return df
    except Exception:
        return None


def _parse_csv_data(path: Path) -> Optional[pd.DataFrame]:
    """Parse CSV/TSV data directly."""
    try:
        # Try CSV first
        df = pd.read_csv(path)
        return df
    except Exception:
        pass
    
    try:
        # Try TSV
        df = pd.read_csv(path, sep='\t')
        return df
    except Exception:
        pass
    
    return None


def _validate_data_quality(df: pd.DataFrame) -> None:
    """Validate data quality and raise warnings if needed."""
    # Check for missing values
    if df.isnull().any().any():
        missing_info = df.isnull().sum()
        missing_cols = missing_info[missing_info > 0]
        print(f"Warning: Missing values found: {missing_cols.to_dict()}")
    
    # Check k values are positive integers
    if not all(df['k'] > 0):
        raise ValueError("All k values must be positive")
    
    if not all(df['k'] == df['k'].astype(int)):
        print("Warning: Non-integer k values found, converting to int")
        df['k'] = df['k'].astype(int)
    
    # Check p_true values are positive
    if not all(df['p_true'] > 0):
        raise ValueError("All p_true values must be positive")
    
    # Check p_hat_z5d values are positive
    if not all(df['p_hat_z5d'] > 0):
        raise ValueError("All p_hat_z5d values must be positive")
    
    # Check data consistency
    if len(df) < 10:
        print(f"Warning: Small dataset with only {len(df)} samples")
    
    # Check for duplicated k values
    if df['k'].duplicated().any():
        duplicated_k = df[df['k'].duplicated()]['k'].unique()
        raise ValueError(f"Duplicated k values found: {duplicated_k}")
    
    print(f"Data validation passed: {len(df)} samples, k range [{df['k'].min()}, {df['k'].max()}]")