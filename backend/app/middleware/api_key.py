from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
from datetime import datetime
import re

class APIKeyValidator:
    def __init__(self):
        pass
    
    async def __call__(self, request: Request):
        # API key header'dan al
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            # JWT token kontrol et
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # JWT token var, devam et
                return
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key or JWT token required"
            )
        
        # API key format kontrol
        if not re.match(r"^pdfai_[A-Za-z0-9_-]{32,}$", api_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid API key format"
            )
        
        # Database'den kontrol et
        db: Session = next(get_db())
        api_key_record = db.query(models.APIKey).filter(
            models.APIKey.api_key == api_key,
            models.APIKey.is_active == True
        ).first()
        
        if not api_key_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive API key"
            )
        
        # Rate limiting kontrol
        from app.middleware import rate_limiter
        if not rate_limiter.check_rate_limit(api_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Update last used
        api_key_record.last_used_at = datetime.utcnow()
        api_key_record.total_requests += 1
        db.commit()
        
        # User bilgisini request'e ekle
        request.state.user_id = api_key_record.user_id
        request.state.api_key = api_key

api_key_validator = APIKeyValidator()