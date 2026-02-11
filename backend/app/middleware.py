from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth import verify_token
from typing import Optional

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            
            username = verify_token(credentials.credentials)
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            
            request.state.username = username
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )

# Rate limiting middleware (basit versiyon)
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def check_rate_limit(self, api_key: str):
        now = time.time()
        minute_ago = now - 60
        
        # Eski request'leri temizle
        self.requests[api_key] = [req_time for req_time in self.requests[api_key] if req_time > minute_ago]
        
        # Rate limit kontrolü
        if len(self.requests[api_key]) >= self.requests_per_minute:
            return False
        
        self.requests[api_key].append(now)
        return True

rate_limiter = RateLimiter()