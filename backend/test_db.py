# test_db.py
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test database connection"""
    print("🧪 Testing database connection...")
    
    # Database URL'ini al
    database_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/pdf_ai"
    )
    
    print(f"Database URL: {database_url}")
    
    try:
        # Engine oluştur
        engine = create_engine(database_url)
        
        # Bağlantı testi
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Tabloları kontrol et
            print("\n📊 Checking tables...")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            if tables:
                print(f"Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("❌ No tables found in database")
                
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        
        # Docker kontrolü
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if Docker is running: docker-compose ps")
        print("2. Start Docker: docker-compose up -d")
        print("3. Check logs: docker logs backend-postgres-1")
        print("4. Wait 10 seconds after starting Docker")
        
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\n🧪 Testing Redis connection...")
    
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        print(f"Redis URL: {redis_url}")
        
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PDF AI Backend Database Test")
    print("=" * 50)
    
    db_ok = test_database_connection()
    redis_ok = test_redis_connection()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"Redis: {'✅ OK' if redis_ok else '❌ FAILED'}")
    
    if db_ok and redis_ok:
        print("\n🎉 All connections working!")
        sys.exit(0)
    else:
        print("\n⚠️ Some connections failed")
        sys.exit(1)