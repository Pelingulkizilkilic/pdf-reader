from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="PDF AI - No 422 Error")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Model - BU KRİTİK!
class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {
        "status": "running",
        "no_422": "yes",
        "message": "Backend fixed for 422 error"
    }

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    print(f"📤 Upload received: {file.filename}")
    return {
        "id": f"pdf-{file.filename}",
        "filename": file.filename,
        "status": "success",
        "pages": 25,
        "ai_ready": True
    }

@app.post("/api/chat/{pdf_id}")
async def chat_with_pdf(pdf_id: str, request: QuestionRequest):
    print(f"💬 Chat request - PDF: {pdf_id}, Q: {request.question}")
    return {
        "answer": f"**✅ BACKEND WORKING!**\n\nPDF ID: {pdf_id}\nQuestion: {request.question}\n\nAI Analysis: This document appears to be well-structured with clear objectives.\n\nStatus: **422 Error FIXED!**",
        "confidence": 0.98,
        "sources": ["Full document analysis"],
        "backend": "FastAPI (no 422)"
    }

if __name__ == "__main__":
    print("="*60)
    print("🚀 BACKEND WITH 422 FIX STARTING...")
    print("✅ Pydantic models added")
    print("✅ No more 422 errors")
    print("📍 http://localhost:8000")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
