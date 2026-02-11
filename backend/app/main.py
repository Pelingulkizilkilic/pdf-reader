# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# First create the app
app = FastAPI(title="PDF AI Assistant", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "PDF AI Assistant API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pdf-ai-backend"}


# Import routers inside startup event to avoid circular imports
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Application starting up...")
    
    try:
        # Import routers HERE (after app is created)
        from app.api.auth import router as auth_router
        from app.api.upload import router as upload_router
        from app.api.ask import router as ask_router
        
        # Include routers
        app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
        app.include_router(upload_router, prefix="/api", tags=["upload"])
        app.include_router(ask_router, prefix="/api", tags=["ask"])
        
        logger.info("✅ All routers imported successfully")
        
        # SIMPLE database check
        try:
            from sqlalchemy import text
            from app.database.database import engine
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("✅ Database connection successful")
                
        except Exception as e:
            logger.warning(f"⚠️ Database connection issue: {e}")
            logger.info("⚠️ Application will continue, but database features may not work")
            
    except ImportError as e:
        logger.error(f"❌ Router import error: {e}")
        # Don't raise, let app start without routers
        pass


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Application shutting down...")


# Test endpoint (no auth required)
@app.get("/test")
async def test_endpoint():
    return {"message": "API is working", "timestamp": "now"}