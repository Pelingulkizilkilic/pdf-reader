# app/database/database.py - FIXED VERSION
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# FIXED: Correct default database URL - pdf_ai NOT pdf_ai_test
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/pdf_ai"  # CHANGED: pdf_ai_test → pdf_ai
)

logger.info(f"🔗 Database URL: {DATABASE_URL}")  # FIXED: Use DATABASE_URL variable

# Try to create engine, but don't crash if it fails
try:
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Show SQL queries
        pool_pre_ping=True
    )
    
    # Test connection immediately
    logger.info("🔄 Testing database connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        logger.info(f"✅ Database test query: {result.scalar()}")
    
    logger.info("🎉 Database engine created successfully")
    
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    
    # Try SQLite as fallback
    logger.info("🔄 Trying SQLite fallback...")
    try:
        sqlite_url = "sqlite:///./pdf_ai.db"
        engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            echo=True
        )
        logger.info(f"✅ Using SQLite: {sqlite_url}")
    except Exception as e2:
        logger.error(f"❌ SQLite also failed: {e2}")
        engine = None

# Create session maker only if engine exists
if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Create tables if SQLite
    if "sqlite" in str(engine.url):
        logger.info("📦 Creating SQLite tables...")
        Base.metadata.create_all(bind=engine)
else:
    SessionLocal = None
    Base = declarative_base()
    logger.warning("⚠️  No database engine available")

def get_db():
    """Database session dependency"""
    if SessionLocal is None:
        # Return dummy session if no database
        class DummySession:
            def close(self): pass
            def commit(self): pass 
            def rollback(self): pass
            def add(self, obj): pass
            def query(self, *args):
                class DummyQuery:
                    def filter(self, *args): return self
                    def first(self): return None
                    def all(self): return []
                    def count(self): return 0
                return DummyQuery()
            def execute(self, *args): 
                class DummyResult:
                    def scalar(self): return None
                return DummyResult()
        
        db = DummySession()
        try:
            yield db
        finally:
            db.close()
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()