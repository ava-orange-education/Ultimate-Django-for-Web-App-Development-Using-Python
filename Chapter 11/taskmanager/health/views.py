from django.core.cache import cache
from django.db import connections
from django.http import JsonResponse


def liveness(request):
    # Perform checks to determine if the app is alive
    return JsonResponse({"status": "alive"})


def readiness(request):
    try:
        # Check database connectivity
        connections["default"].cursor()

        # Check cache (e.g., Redis) connectivity
        cache.set("health_check", "ok", timeout=10)
        if cache.get("health_check") != "ok":
            raise ValueError("Failed to communicate with cache backend")

        return JsonResponse({"status": "healthy"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=500)
