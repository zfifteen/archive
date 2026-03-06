# PhiFilterClient SDK Documentation

The `PhiFilterClient` provides a robust Python interface for interacting with the Phi-Harmonic Trading Filter API. It supports both synchronous and asynchronous operations, making it suitable for a wide range of trading application architectures.

## Installation

Ensure you have `httpx` installed:

```bash
pip install httpx
```

## Quick Start

```python
from src.sdk.client import PhiFilterClient

# Initialize the client
client = PhiFilterClient(api_key="your_api_key_here", base_url="http://localhost:8000")

# Filter a single signal
result = client.filter_signal(
    price=100.0,
    support=95.0,
    resistance=105.0,
    atr=2.0
)

if result['passed']:
    print(f"Signal passed with {result['confidence']*100}% confidence")
else:
    print(f"Signal rejected: {result['rejection_reason']}")
```

## Features

### Synchronous and Asynchronous Support
Every method in the SDK has an `async` counterpart (e.g., `filter_signal` and `filter_signal_async`).

### Batch Processing
Efficiently process multiple signals in one network round-trip.

```python
signals = [
    {"price": 100.0, "support": 95.0, "resistance": 105.0, "atr": 2.0},
    {"price": 110.0, "support": 95.0, "resistance": 105.0, "atr": 2.0}
]

batch_results = client.filter_batch(signals)
for i, res in enumerate(batch_results['results']):
    print(f"Signal {i}: {'Passed' if res['passed'] else 'Rejected'}")
```

### Usage Monitoring
Track your API consumption and remaining rate limits.

```python
usage = client.get_usage()
print(f"Total requests: {usage['total_requests']}")
print(f"Rate limit remaining: {usage['rate_limit_remaining']}")
```

## API Reference

### `PhiFilterClient(api_key: str, base_url: str)`
- `api_key`: Your unique API key.
- `base_url`: The URL of the Phi-Filter API instance.

### Methods

| Sync Method | Async Method | Description |
|-------------|--------------|-------------|
| `filter_signal(...)` | `filter_signal_async(...)` | Filter a single price signal. |
| `filter_batch(...)` | `filter_batch_async(...)` | Filter multiple signals in one request. |
| `get_usage()` | `get_usage_async()` | Get your account's usage statistics. |
| `get_stats()` | `get_stats_async()` | Get global filter performance stats. |
