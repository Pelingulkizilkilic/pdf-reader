# PDF AI Assistant Backend - ORİJİNAL
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from datetime import datetime

app = FastAPI()

# CORS - SİZİN ORİJİNAL AYARLARINIZ
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

# Health check - SİZİN ORİJİNAL ENDPOINT'İNİZ
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "pdf-ai-backend",
        "timestamp": datetime.now().isoformat()
    }

# Upload endpoint - SİZİN ORİJİNAL YAPINIZ
@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(400, "Only PDF files allowed")
        
        # Burada sizin orijinal PDF işleme kodunuz olacak
        file_id = f"pdf_{int(datetime.now().timestamp())}"
        
        return {
            "id": file_id,
            "filename": file.filename,
            "message": "PDF uploaded successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(500, f"Upload error: {str(e)}")

# Chat endpoint - SİZİN ORİJİNAL AI KODUNUZ
@app.post("/api/chat")
async def chat_with_pdf(request: ChatRequest):
    try:
        # Burada sizin orijinal AI/PDF analiz kodunuz olacak
        return {
            "answer": f"PDF {request.pdfId} analiz edildi: {request.question}",
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "source": "Orijinal Backend"
        }
    except Exception as e:
        raise HTTPException(500, f"Chat error: {str(e)}")

if __name__ == "__main__":
    print("🚀 ORİJİNAL BACKEND BAŞLATILIYOR")
    print("📍 http://localhost:5000")  # SİZİN ORİJİNAL PORTUNUZ
    uvicorn.run(app, host="0.0.0.0", port=5000)
