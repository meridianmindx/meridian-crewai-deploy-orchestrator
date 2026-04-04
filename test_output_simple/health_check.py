#!/usr/bin/env python3
"""Health Check Endpoint for CrewAI Agent"""

from fastapi import FastAPI
import psutil
import time
from typing import Dict, Any

app = FastAPI()
START_TIME = time.time()
request_count = 0

@app.on_event("startup")
async def startup_event():
    print("Health check service started")

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    global request_count
    request_count += 1
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        uptime = time.time() - START_TIME
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime_seconds": round(uptime, 2),
            "memory_percent": memory.percent,
            "cpu_percent": cpu,
            "request_count": request_count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

@app.get("/metrics")
async def metrics() -> str:
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        uptime = time.time() - START_TIME
        return f"""# HELP agent_uptime_seconds Agent uptime
# TYPE agent_uptime_seconds counter
agent_uptime_seconds {uptime}
# HELP agent_memory_percent Memory usage
# TYPE agent_memory_percent gauge
agent_memory_percent {memory.percent}
# HELP agent_cpu_percent CPU usage
# TYPE agent_cpu_percent gauge
agent_cpu_percent {cpu}
# HELP agent_requests_total Total requests
# TYPE agent_requests_total counter
agent_requests_total {request_count}
"""
    except Exception as e:
        return f"# ERROR: {str(e)}"

@app.get("/ready")
async def readiness_check() -> Dict[str, str]:
    return {"status": "ready"}

@app.get("/live")
async def liveness_check() -> Dict[str, str]:
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
