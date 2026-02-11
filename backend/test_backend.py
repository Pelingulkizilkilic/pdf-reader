import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime

os.environ["OPENAI_API_KEY"] = "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"

app = FastAPI()

# GENİŞ CORS AYARLARI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm origin'lere izin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class ChatRequest(BaseModel):
    pdfId: str
    question: str

@app.get("/api/health")
async def health():
    return {"status": "online", "cors": "enabled_for_all"}

@app.options("/api/{path:path}")
async def options_handler(path: str):
    """CORS preflight için"""
    return {}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    print(f"📨 Chat request: {request.question}")
    return {
        "answer": f"✅ BACKEND ÇALIŞIYOR!\n\nSoru: {request.question}\nPDF: {request.pdfId}\n\nBu OpenAI GPT-4'ten geliyor.",
        "question": request.question,
        "pdfId": request.pdfId,
        "timestamp": datetime.now().isoformat(),
        "source": "Test Backend"
    }

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    return {
        "id": "test_id",
        "filename": file.filename,
        "message": "Upload test başarılı"
    }

if __name__ == "__main__":
    print("🚀 TEST BACKEND (CORS FIXED)")
    print("📍 http://localhost:8000")
    print("🔓 CORS: Tüm origin'lere açık")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
