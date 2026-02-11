# check.py
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("🔍 Checking configuration...")
print("=" * 50)

# 1. Check .env file
env_path = ".env"
if os.path.exists(env_path):
    print(f"✅ .env file exists: {os.path.abspath(env_path)}")
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Find DATABASE_URL
    import re
    match = re.search(r'DATABASE_URL\s*=\s*(.+)', content)
    if match:
        db_url = match.group(1).strip()
        print(f"📦 DATABASE_URL in .env: {db_url}")
        
        if "pdf_ai_test" in db_url:
            print("❌ PROBLEM: Database URL contains 'pdf_ai_test'")
            print("💡 Change it to 'pdf_ai' in .env file")
        elif "sqlite" in db_url:
            print("✅ Using SQLite (good choice for development)")
        elif "pdf_ai" in db_url:
            print("✅ Using PostgreSQL with 'pdf_ai' database")
        else:
            print("⚠️  Unknown database URL format")
    else:
        print("❌ DATABASE_URL not found in .env")
else:
    print("❌ .env file not found")

print("\n" + "=" * 50)
print("💡 QUICK FIXES:")
print("1. Edit .env: Change DATABASE_URL to use 'pdf_ai' not 'pdf_ai_test'")
print("2. Or use SQLite: DATABASE_URL=sqlite:///./pdf_ai.db")
print("3. Edit database.py: Change default URL to 'pdf_ai'")
print("=" * 50)

# Check database.py
db_py_path = "app/database/database.py"
if os.path.exists(db_py_path):
    with open(db_py_path, 'r') as f:
        db_content = f.read()
    
    if "pdf_ai_test" in db_content:
        print("\n⚠️  database.py still contains 'pdf_ai_test' in default URL")
        print("💡 Edit: app/database/database.py line ~10")