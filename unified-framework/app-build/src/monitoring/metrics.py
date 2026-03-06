"""
Metrics collection for the Phi-Harmonic Trading Filter API
"""

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
import time

# Custom metrics
signals_filtered_total = Counter(
    "phi_signals_filtered_total",
    "Total number of signals filtered",
    ["status", "endpoint"],
)

filter_duration = Histogram(
    "phi_filter_duration_seconds", "Time spent filtering signals", ["endpoint"]
)

redis_operations_total = Counter(
    "phi_redis_operations_total", "Total Redis operations", ["operation", "status"]
)


def setup_metrics(app):
    """Initialize Prometheus metrics for API monitoring"""
    # Instrument FastAPI app
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        excluded_handlers=["/metrics", "/health"],
    )
    instrumentator.instrument(app).expose(app, endpoint="/metrics")

    # Custom metrics are already defined above
