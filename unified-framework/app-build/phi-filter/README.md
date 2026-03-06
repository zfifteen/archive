# Phi-Filter SaaS

A high-performance geometric filtering API for trading signals.

## Quick Start

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the API:
   ```bash
   uvicorn src.api.main:app --reload
   ```
3. Test the health check:
   ```bash
   curl http://localhost:8000/
   ```

### Running Tests
1. Install test dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
2. Run all tests:
   ```bash
   python3 -m unittest discover tests
   ```

## API Documentation
Once the API is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints
- `POST /filter`: Apply geometric filtering to a single signal.
- `POST /filter/batch`: Process multiple signals (up to 100) in a single request.
- `POST /filter/fibonacci`: Filter Fibonacci levels.
- `GET /usage`: Check your API key usage and rate limits.
- `GET /stats`: Global filter performance statistics.

## Interactive Dashboard
A Streamlit-based dashboard for real-time signal visualization and harmonic lattice exploration.

### Running the Dashboard
1. Ensure the API is running (see Quick Start).
2. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```
3. Open your browser to the provided URL (typically `http://localhost:8501`).

### Features
- **Signal Filtering**: Test individual signals with real-time results.
- **Harmonic Lattice**: Visualize and explore geometrically feasible price levels.
- **Batch Analysis**: Upload CSV files for bulk signal processing.
- **Usage Monitoring**: Track API usage and rate limits.

## Client SDK
A Python SDK is included in the `src/sdk/` directory.

### Example Usage (Async)
```python
from src.sdk import PhiFilterClient
import asyncio

async def main():
    client = PhiFilterClient(api_key="your_key_here")
    
    # Filter a single signal
    result = await client.filter_signal_async(
        price=150.25, support=148.0, resistance=155.0, atr=2.5
    )
    print(f"Passed: {result['passed']}")

    # Batch process
    batch_signals = [
        {"price": 100.0, "support": 95.0, "resistance": 105.0, "atr": 2.0},
        {"price": 110.0, "support": 95.0, "resistance": 105.0, "atr": 2.0}
    ]
    batch_results = await client.filter_batch_async(batch_signals)
    print(f"Batch results: {batch_results}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Architecture
- `src/core/`: Core geometric filtering logic.
- `src/api/`: FastAPI REST interface and authentication.
- `src/sdk/`: Python client SDK.
- `tests/`: Unit and integration tests.
