# test_db_fixed.py
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

load_dotenv()

def main():
    print("🚀 PDF AI Database Connection Test")
    print("=" * 50)
    
    # Doğru database URL (docker-compose.yml ile aynı)
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/pdf_ai"
    print(f"Database URL: {DATABASE_URL}")
    
    try:
        # Engine oluştur
        engine = create_engine(DATABASE_URL, echo=True)
        
        print("\n🔗 Connecting to database...")
        with engine.connect() as conn:
            # Version kontrolü
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ PostgreSQL version: {version}")
            
            # Database ismi
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✅ Database name: {db_name}")
            
            # Tabloları listele
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
            
            # Kullanıcıları kontrol et
            if 'users' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                print(f"✅ Users in database: {user_count}")
                
                result = conn.execute(text("SELECT username, email FROM users"))
                print("   Users:")
                for row in result:
                    print(f"   - {row.username} ({row.email})")
            
            print("\n🎉 DATABASE CONNECTION SUCCESSFUL!")
            return True
            
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        
        print("\n🔧 Troubleshooting:")
        print("1. Check Docker is running: docker-compose ps")
        print("2. Check .env file has: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pdf_ai")
        print("3. Wait a few seconds after Docker starts")
        
        return False

if __name__ == "__main__":
    # Biraz bekle (database tam hazır olsun)
    print("⏳ Waiting 5 seconds for database...")
    time.sleep(5)
    
    success = main()
    sys.exit(0 if success else 1)