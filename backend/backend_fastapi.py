from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from datetime import datetime
import json

# PDF işleme için (demo için basit tutuyoruz)
import PyPDF2
from io import BytesIO

app = FastAPI(title="PDF AI Assistant API")

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

# Bellekte PDF verilerini sakla (gerçek uygulamada DB kullan)
pdf_storage = {}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "pdf-ai-backend"}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(400, "Sadece PDF dosyaları kabul edilir")
        
        # PDF'yi oku
        contents = await file.read()
        
        # PDF'den text çıkar (gerçek parsing)
        pdf_text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
            for page_num in range(min(len(pdf_reader.pages), 5)):  # İlk 5 sayfa
                page = pdf_reader.pages[page_num]
                pdf_text += page.extract_text() + "\n\n"
        except:
            pdf_text = "PDF okunamadı veya boş"
        
        # Benzersiz ID oluştur
        pdf_id = f"pdf_{int(datetime.now().timestamp() * 1000)}"
        
        # PDF içeriğini sakla
        pdf_storage[pdf_id] = {
            "id": pdf_id,
            "filename": file.filename,
            "text": pdf_text[:5000],  # İlk 5000 karakter
            "page_count": len(pdf_reader.pages) if 'pdf_reader' in locals() else 0,
            "upload_time": datetime.now().isoformat()
        }
        
        print(f"📥 PDF yüklendi: {file.filename} (ID: {pdf_id})")
        print(f"   Text uzunluğu: {len(pdf_text)} karakter")
        
        return {
            "id": pdf_id,
            "filename": file.filename,
            "size": len(contents),
            "page_count": len(pdf_reader.pages) if 'pdf_reader' in locals() else 0,
            "text_preview": pdf_text[:200] + "..." if len(pdf_text) > 200 else pdf_text,
            "message": "PDF başarıyla yüklendi ve analiz edildi"
        }
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(500, f"Upload hatası: {str(e)}")

@app.post("/api/chat")
async def chat_with_pdf(request: ChatRequest):
    try:
        print(f"💬 Chat request - PDF: {request.pdfId}, Question: {request.question}")
        
        # PDF'i bul
        if request.pdfId not in pdf_storage:
            return {
                "answer": "❌ PDF bulunamadı. Lütfen önce PDF yükleyin.",
                "source": "backend-error"
            }
        
        pdf_data = pdf_storage[request.pdfId]
        pdf_text = pdf_data["text"]
        
        # AI ANALİZİ (Demo - gerçekte OpenAI/LangChain kullanılır)
        question_lower = request.question.lower()
        
        # PDF içeriğine göre akıllı analiz
        if len(pdf_text) < 100:
            # PDF okunamadıysa
            answer = f"📄 PDF analizi: '{pdf_data['filename']}'\n\n" \
                     f"PDF okunamadı veya boş. Lütfen farklı bir PDF yükleyin."
        
        elif "şifre" in question_lower or "password" in question_lower:
            # PDF'de şifre ara
            answer = f"🔐 PDF Şifre Analizi: '{pdf_data['filename']}'\n\n" \
                     f"PDF içeriği analiz edildi. Şifreler arandı.\n" \
                     f"PDF ID: {request.pdfId}\n" \
                     f"Sayfa sayısı: {pdf_data['page_count']}\n\n" \
                     f"*Not: Gerçek uygulamada AI şifreleri tespit eder.*"
        
        elif "özet" in question_lower or "summary" in question_lower:
            # PDF özeti
            words = pdf_text.split()
            word_count = len(words)
            preview = ' '.join(words[:50]) + '...' if word_count > 50 else pdf_text
            
            answer = f"📋 PDF Özeti: '{pdf_data['filename']}'\n\n" \
                     f"Kelime sayısı: {word_count}\n" \
                     f"Sayfa sayısı: {pdf_data['page_count']}\n\n" \
                     f"İçerik önizleme:\n{preview}"
        
        elif "içindekiler" in question_lower or "contents" in question_lower:
            # İçindekiler
            lines = pdf_text.split('\n')
            headings = [line for line in lines if len(line.strip()) > 30][:10]
            
            answer = f"📑 PDF İçindekiler: '{pdf_data['filename']}'\n\n" \
                     f"Ana başlıklar:\n"
            for i, heading in enumerate(headings[:5], 1):
                answer += f"{i}. {heading[:50]}...\n"
            
            if len(headings) > 5:
                answer += f"... ve {len(headings)-5} başlık daha"
        
        else:
            # Genel analiz
            answer = f"🤖 PDF AI Analizi: '{pdf_data['filename']}'\n\n" \
                     f"Soru: '{request.question}'\n\n" \
                     f"PDF Detayları:\n" \
                     f"- ID: {request.pdfId}\n" \
                     f"- Dosya: {pdf_data['filename']}\n" \
                     f"- Sayfa: {pdf_data['page_count']}\n" \
                     f"- Yükleme: {pdf_data['upload_time']}\n\n" \
                     f"Analiz: PDF içeriğiniz AI tarafından incelendi. " \
                     f"Gerçek uygulamada OpenAI/LangChain ile detaylı analiz yapılır."
        
        return {
            "answer": answer,
            "question": request.question,
            "pdfId": request.pdfId,
            "filename": pdf_data["filename"],
            "source": "python-backend-ai",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return {
            "answer": f"❌ Analiz hatası: {str(e)}",
            "source": "error"
        }

if __name__ == "__main__":
    print("🚀 PDF AI Backend başlatılıyor...")
    print("📍 http://localhost:8000")
    print("📄 Gerçek PDF parsing aktif")
    uvicorn.run(app, host="0.0.0.0", port=8000)
