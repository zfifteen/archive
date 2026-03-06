"""
Health checks for the Phi-Harmonic Trading Filter API
"""

from datetime import datetime
from ..config.settings import settings


# TEMPLATE_BEGIN
# PURPOSE: Perform comprehensive health check including dependencies
# INPUTS: N/A
# PROCESS:
#   STEP[1]: Check Redis connectivity and response time
#   STEP[2]: Verify core algorithm performance (<1μs)
#   STEP[3]: Test database connectivity if available
#   STEP[4]: Check system resources (memory, CPU)
#   STEP[5]: Return detailed health status with component statuses
# OUTPUTS: dict with health status, components, and metrics
# DEPENDENCIES: redis client; core filter module; psutil for system metrics
# TEMPLATE_END
def comprehensive_health_check():
    """Perform comprehensive health check including dependencies"""
    import psutil
    from ..auth.dependencies import get_redis_client
    from ..core.filter import phi_harmonic_filter
    import time

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": settings.version,
        "components": {},
        "metrics": {},
    }

    # Check Redis
    try:
        redis_client = get_redis_client()
        start_time = time.time()
        redis_client.ping()
        redis_time = time.time() - start_time
        health_status["components"]["redis"] = {
            "status": "healthy",
            "response_time_ms": round(redis_time * 1000, 2),
        }
    except Exception as e:
        health_status["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check core algorithm performance
    try:
        start_time = time.time()
        result = phi_harmonic_filter(100.0, 95.0, 105.0, 2.0)
        algo_time = time.time() - start_time
        health_status["components"]["algorithm"] = {
            "status": "healthy",
            "execution_time_us": round(algo_time * 1_000_000, 2),
            "test_result": result,
        }
        if algo_time > 0.00001:  # >10μs
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["algorithm"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "unhealthy"

    # System resources
    health_status["metrics"]["cpu_percent"] = psutil.cpu_percent(interval=1)
    health_status["metrics"]["memory_percent"] = psutil.virtual_memory().percent
    health_status["metrics"]["disk_percent"] = psutil.disk_usage("/").percent

    return health_status
