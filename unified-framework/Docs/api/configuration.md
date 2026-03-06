# API Configuration

Configuration options and settings for the Z Framework API.

## Overview

This document describes the configuration parameters and options available for customizing the Z Framework API behavior.

## Configuration Files

### Main Configuration
- **File**: `config/api_config.json`
- **Purpose**: Primary API configuration
- **Format**: JSON

### Environment Variables
- **Z_FRAMEWORK_PRECISION**: Decimal precision (default: 50)
- **Z_FRAMEWORK_VALIDATION**: Validation mode (strict|normal|minimal)
- **Z_FRAMEWORK_CACHE**: Enable computation caching (true|false)

## Configuration Parameters

### Precision Settings
```json
{
  "precision": {
    "mpmath_dps": 50,
    "validation_threshold": 1e-16,
    "bootstrap_samples": 1000
  }
}
```

### Performance Settings
```json
{
  "performance": {
    "enable_parallel": true,
    "max_workers": 4,
    "cache_size": 1000
  }
}
```

### Validation Settings
```json
{
  "validation": {
    "enable_precision_checks": true,
    "require_bootstrap_ci": true,
    "statistical_significance": 1e-6
  }
}
```

## Usage

### Loading Configuration
```python
from src.api.config import load_config

config = load_config('config/api_config.json')
```

### Environment Setup
```bash
export Z_FRAMEWORK_PRECISION=50
export Z_FRAMEWORK_VALIDATION=strict
```

## See Also

- [API Reference](reference.md)
- [Extensions](extensions.md)