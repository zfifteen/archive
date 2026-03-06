import asyncio
import sys
import os

# Add src to path for local demonstration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sdk.client import PhiFilterClient

async def main():
    # Note: In a real app, use environment variables for API keys
    client = PhiFilterClient(api_key="demo-key-123", base_url="http://localhost:8000")
    
    print("--- Single Signal Filter (Sync) ---")
    try:
        # This will fail if the server is not running, but demonstrates usage
        res = client.filter_signal(100.0, 95.0, 105.0, 2.0)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Server offline or error: {e}")

    print("
--- Batch Signal Filter (Async) ---")
    signals = [
        {"price": 102.5, "support": 95.0, "resistance": 105.0, "atr": 2.0},
        {"price": 108.0, "support": 95.0, "resistance": 105.0, "atr": 2.0}
    ]
    try:
        res = await client.filter_batch_async(signals)
        for i, r in enumerate(res['results']):
            status = "PASS" if r['passed'] else f"REJECT ({r['rejection_reason']})"
            print(f"Signal {i}: {status}")
    except Exception as e:
        print(f"Server offline or error: {e}")

if __name__ == "__main__":
    # Ensure the examples directory exists if running manually
    asyncio.run(main())
