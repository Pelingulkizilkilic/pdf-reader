import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime
import tempfile
import PyPDF2
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

# OpenAI API Key (gerçek projede .env'den al)
os.environ["OPENAI_API_KEY"] = "sk-proj-your-key-here"  # BURAYA KENDİ KEY'İNİZİ KOYUN

app = FastAPI(title="PDF AI Assistant Pro")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modeller
class ChatRequest(BaseModel):
    pdfId: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    question: str
    pdfId: str
    timestamp: str
    confidence: float

# AI Model
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.3,
    max_tokens=1000
)

# PDF'den metin çıkarma
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"
        return text[:5000]  # İlk 5000 karakter
    except Exception as e:
        return f"PDF okuma hatası: {str(e)}"

# Bellekte PDF depolama (demo için)
pdf_storage = {}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "PDF AI Pro",
        "ai_model": "gpt-4-turbo",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(400, "Sadece PDF dosyaları")
        
        # PDF'i geçici dosyaya kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # PDF'den metin çıkar
        with open(tmp_path, 'rb') as f:
            pdf_text = extract_text_from_pdf(f)
        
        # Depola
        file_id = f"pdf_{int(datetime.now().timestamp())}"
        pdf_storage[file_id] = {
            "filename": file.filename,
            "text": pdf_text,
            "upload_time": datetime.now().isoformat(),
            "text_length": len(pdf_text)
        }
        
        # Geçici dosyayı sil
        os.unlink(tmp_path)
        
        print(f"PDF yüklendi: {file.filename}, Metin uzunluğu: {len(pdf_text)}")
        
        return {
            "id": file_id,
            "filename": file.filename,
            "size": len(content),
            "text_preview": pdf_text[:200] + "...",
            "message": "PDF başarıyla yüklendi ve AI için hazırlandı"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Yükleme hatası: {str(e)}")

@app.post("/api/chat")
async def chat_with_pdf(request: ChatRequest):
    try:
        print(f"AI Soru: {request.question} (PDF: {request.pdfId})")
        
        # PDF içeriğini al
        pdf_data = pdf_storage.get(request.pdfId)
        
        if not pdf_data:
            # Demo mod - örnek PDF içeriği
            pdf_content = """
            GİZLİ PROJE X RAPORU
            Hazırlayan: Dr. Ahmet Yılmaz - Araştırma Direktörü
            Tarih: 15 Ocak 2024
            Şifre: Mavi Kelebek
            Proje Yöneticisi: Kediler Alemi Başkanı Tekir
            Bütçe: 1.000.000 TL
            Durum: Aktif
            
            Özet: Bu rapor, Proje X'in gelişim aşamalarını ve 
            başarı metriklerini detaylandırmaktadır.
            """
        else:
            pdf_content = pdf_data["text"]
            print(f"Gerçek PDF içeriği kullanılıyor: {len(pdf_content)} karakter")
        
        # AI'ya gönderilecek sistem mesajı
        system_message = SystemMessage(content=f"""
        Sen bir PDF analiz uzmanısın. Kullanıcının yüklediği PDF dosyasının içeriği:
        
        {pdf_content[:4000]}
        
        YANITLAMA KURALLARI:
        1. Sadece verilen PDF içeriğine dayanarak cevap ver
        2. Eğer PDF'de bilgi yoksa "Bu bilgi PDF'de bulunmuyor" de
        3. PDF'den alıntı yap
        4. Türkçe cevap ver
        5. Detaylı ve açıklayıcı ol
        """)
        
        # Kullanıcı mesajı
        human_message = HumanMessage(content=request.question)
        
        # AI'ya sor
        response = llm.invoke([system_message, human_message])
        
        ai_answer = response.content
        
        return {
            "answer": ai_answer,
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.9,
            "source": "OpenAI GPT-4 Turbo",
            "context_used": len(pdf_content) > 0
        }
        
    except Exception as e:
        print(f"AI hatası: {e}")
        # Fallback cevap
        return {
            "answer": f"⚠️ AI işleme hatası: {str(e)}\n\nDemo cevap: PDF analiz edilemedi. Lütfen OpenAI API key'inizi kontrol edin.",
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.1,
            "source": "Error Fallback"
        }

if __name__ == "__main__":
    print("🚀 AI PDF ASSISTANT PRO")
    print("📍 http://localhost:8000")
    print("🤖 Model: GPT-4 Turbo")
    print("═" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
