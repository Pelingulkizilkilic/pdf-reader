# test_database_final.py
import os
import sys
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import subprocess

load_dotenv()

def check_docker():
    """Check Docker containers"""
    print("🔍 Checking Docker...")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print(result.stdout)
        
        if "pdf_ai_postgres" in result.stdout and "Up" in result.stdout:
            print("✅ PostgreSQL container is running")
            return True
        else:
            print("❌ PostgreSQL container not found or not running")
            return False
            
    except Exception as e:
        print(f"❌ Docker check failed: {e}")
        return False

def test_postgres_connection():
    """Test PostgreSQL connection"""
    print("\n🧪 Testing PostgreSQL connection...")
    
    # Try multiple connection URLs
    test_urls = [
        ("Main DB", "postgresql://postgres:postgres@localhost:5432/pdf_ai"),
        ("Default DB", "postgresql://postgres:postgres@localhost:5432/postgres"),
        ("Direct from .env", os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pdf_ai"))
    ]
    
    for name, url in test_urls:
        print(f"\nTrying: {name}")
        print(f"URL: {url}")
        
        try:
            engine = create_engine(url, echo=False)
            with engine.connect() as conn:
                # Test 1: Version
                result = conn.execute(text("SELECT version()"))
                print(f"✅ PostgreSQL: {result.scalar().split(',')[0]}")
                
                # Test 2: Database name
                result = conn.execute(text("SELECT current_database()"))
                print(f"✅ Database: {result.scalar()}")
                
                # Test 3: List tables
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                print(f"✅ Tables: {len(tables)} tables found")
                if tables:
                    for table in tables:
                        print(f"   - {table}")
                
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    return False

def check_env_file():
    """Check .env file"""
    print("\n📄 Checking .env file...")
    
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
        
        if "DATABASE_URL" in content:
            print("✅ .env file exists and has DATABASE_URL")
            
            # Extract DATABASE_URL
            for line in content.split('\n'):
                if line.startswith("DATABASE_URL="):
                    print(f"   Found: {line[:60]}...")
                    return True
        else:
            print("❌ DATABASE_URL not found in .env")
            return False
    else:
        print("❌ .env file not found")
        return False

def main():
    print("🚀 PDF AI Database Connection Debug")
    print("=" * 60)
    
    # Step 1: Check Docker
    docker_ok = check_docker()
    
    if not docker_ok:
        print("\n📦 Attempting to start Docker...")
        try:
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            print("⏳ Waiting 10 seconds for PostgreSQL to start...")
            time.sleep(10)
            docker_ok = check_docker()
        except Exception as e:
            print(f"❌ Failed to start Docker: {e}")
    
    # Step 2: Check .env
    env_ok = check_env_file()
    
    # Step 3: Test connection
    print("\n" + "=" * 60)
    connection_ok = test_postgres_connection()
    
    # Results
    print("\n" + "=" * 60)
    print("📊 DEBUG RESULTS:")
    print(f"Docker running: {'✅ YES' if docker_ok else '❌ NO'}")
    print(f".env configured: {'✅ YES' if env_ok else '❌ NO'}")
    print(f"Database connected: {'✅ YES' if connection_ok else '❌ NO'}")
    
    if connection_ok:
        print("\n🎉 Database is ready! Starting server should work now.")
        print("🚀 Run: uvicorn app.main:app --reload")
        return 0
    else:
        print("\n🔧 MANUAL FIX STEPS:")
        print("1. Start Docker Desktop")
        print("2. Run: docker-compose up -d")
        print("3. Wait 15 seconds")
        print("4. Run: docker-compose ps (check if postgres is Up)")
        print("5. Check .env file has: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pdf_ai")
        print("6. Test manually: docker exec -it pdf_ai_postgres psql -U postgres -d pdf_ai")
        return 1

if __name__ == "__main__":
    sys.exit(main())