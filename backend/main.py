from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import tempfile
import io
from datetime import datetime

# PDF İşleme - Hata vermemesi için korumalı import
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# OpenAI - LangChain hatasını engellemek için doğrudan OpenAI istemcisi
try:
    from openai import OpenAI
    AI_AVAILABLE = True
    # ÖNEMLİ: API anahtarını buraya tırnak içine de yazabilirsin (Test için)
    # client = OpenAI(api_key="sk-proj-BURAYA_YAZABİLİRSİN")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-proj-GECERSIZ"))
except Exception as e:
    AI_AVAILABLE = False
    print(f"⚠️ OpenAI başlatılamadı: {e}")

app = FastAPI(title="PDF AI Assistant")

# CORS - Frontend (3000) ile Backend (8000) haberleşmesi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme aşamasında her şeye izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bellekte PDF depolama
pdf_store = {}

class ChatRequest(BaseModel):
    pdfId: str
    question: str

def extract_text_from_pdf(file_bytes):
    """PDF'den metni güvenli bir şekilde çıkarır"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        # Sayfa sınırını kaldırabiliriz veya ilk 20 sayfa yapabiliriz
        for page in pdf_reader.pages[:20]:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF okuma hatası: {e}")
        return ""

@app.get("/api/health")
async def health():
    return {"status": "ok", "ai": AI_AVAILABLE}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Sadece PDF dosyaları yüklenebilir.")
    
    content = await file.read()
    text = extract_text_from_pdf(content)
    
    if not text.strip():
        raise HTTPException(400, "PDF içeriği okunamadı (Resim formatında olabilir).")

    file_id = f"pdf_{int(datetime.now().timestamp())}"
    pdf_store[file_id] = {
        "filename": file.filename,
        "text": text
    }
    
    return {"id": file_id, "message": "PDF başarıyla işlendi."}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if request.pdfId not in pdf_store:
        return {"answer": "Lütfen önce bir PDF yükleyin."}
    
    pdf_text = pdf_store[request.pdfId]["text"]
    
    try:
        # OpenAI'ya gerçek isteği atıyoruz
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Daha hızlı ve ucuz
            messages=[
                {"role": "system", "content": "Sen bir döküman analiz asistanısın. Sadece verilen metne göre cevap ver."},
                {"role": "user", "content": f"Döküman:\n{pdf_text[:10000]}\n\nSoru: {request.question}"}
            ],
            temperature=0.3
        )
        answer = response.choices[0].message.content
        return {"answer": answer}
    
    except Exception as e:
        print(f"OpenAI Hatası: {e}")
        return {"answer": f"Bir hata oluştu: {str(e)}"}

if __name__ == "__main__":
    # PowerShell'de logları görmek için log_level="info"
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")