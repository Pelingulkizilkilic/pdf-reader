# tests/conftest.py
import sys
import os

# Python path'ini düzelt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, close_all_sessions
from app.main import app
from app.database.database import Base, get_db
import logging
import tempfile

# Logging'ı minimal yap
logging.basicConfig(level=logging.WARNING)

# Memory SQLite kullan (daha temiz)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database in memory"""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    
    # Tabloları oluştur
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Temizlik
    close_all_sessions()
    engine.dispose()


@pytest.fixture
async def async_client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Basit test verisi
@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123"
    }