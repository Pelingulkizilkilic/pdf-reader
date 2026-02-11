# app/middleware/rate_limit.py
import redis
import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379/0",
        requests_per_minute: int = 60,  # Free tier
        requests_per_hour: int = 1000,  # Normal users
        requests_per_day: int = 10000   # Power users
    ):
        super().__init__(app)
        self.redis_client = redis.from_url(redis_url)
        self.limits = {
            "minute": (requests_per_minute, 60),
            "hour": (requests_per_hour, 3600),
            "day": (requests_per_day, 86400)
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get user identifier (API key, JWT token, or IP)
        user_id = self._get_user_identifier(request)
        
        # Check rate limits
        for period, (limit, window) in self.limits.items():
            key = f"rate_limit:{user_id}:{period}"
            current = self.redis_client.get(key)
            
            if current and int(current) >= limit:
                logger.warning(f"Rate limit exceeded: {user_id} - {period}")
                
                # Calculate retry after
                ttl = self.redis_client.ttl(key)
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {limit}/{period}",
                        "retry_after": ttl,
                        "period": period
                    },
                    headers={"Retry-After": str(ttl)}
                )
        
        # Increment counters
        for period, (limit, window) in self.limits.items():
            key = f"rate_limit:{user_id}:{period}"
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            pipe.execute()
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        # Add rate limit headers
        for period, (limit, window) in self.limits.items():
            key = f"rate_limit:{user_id}:{period}"
            current = self.redis_client.get(key) or 0
            remaining = max(0, limit - int(current))
            
            response.headers[f"X-RateLimit-{period.capitalize()}-Limit"] = str(limit)
            response.headers[f"X-RateLimit-{period.capitalize()}-Remaining"] = str(remaining)
            response.headers[f"X-RateLimit-{period.capitalize()}-Reset"] = str(self.redis_client.ttl(key))
        
        return response
    
    def _get_user_identifier(self, request: Request) -> str:
        """Get unique user identifier for rate limiting"""
        # 1. Try API key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # 2. Try JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            return f"token:{token}"
        
        # 3. Fallback to IP address (least reliable)
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"