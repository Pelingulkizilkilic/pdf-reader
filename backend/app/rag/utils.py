import uuid
import hashlib
from datetime import datetime
import os

def generate_pdf_id(filename: str, content: bytes) -> str:
    """PDF için benzersiz ID oluştur"""
    # Dosya adı ve içeriğe göre hash oluştur
    hash_input = f"{filename}_{content[:1000]}"  # İlk 1000 byte
    return hashlib.md5(hash_input.encode()).hexdigest()

def save_pdf_file(file_content: bytes, filename: str) -> str:
    """PDF'i diske kaydet"""
    # Benzersiz dosya adı oluştur
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{filename}"
    filepath = os.path.join("uploads", safe_filename)
    
    with open(filepath, "wb") as f:
        f.write(file_content)
    
    return filepath

def get_pdf_info(pdf_id: str, filename: str) -> dict:
    """PDF bilgilerini döndür"""
    return {
        "id": pdf_id,
        "filename": filename,
        "uploaded_at": datetime.now().isoformat(),
        "status": "processed"
    }