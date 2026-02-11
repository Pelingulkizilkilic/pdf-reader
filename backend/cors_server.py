from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# CORS AYARLARI (KRİTİK!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class Question(BaseModel):
    question: str

@app.get("/")
def home():
    return {
        "status": "running", 
        "cors": "enabled",
        "frontend": "http://localhost:3000"
    }

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    print(f"📥 Received: {file.filename}")
    return {
        "id": f"real-{file.filename}",
        "filename": file.filename,
        "status": "uploaded",
        "cors": "working"
    }

@app.post("/api/chat/{pdf_id}")
async def chat(pdf_id: str, question: Question):
    print(f"💬 Chat: {pdf_id} - {question.question}")
    return {
        "answer": f"✅ **BACKEND-FRONTEND CONNECTED!**\n\nPDF: {pdf_id}\nQ: {question.question}\n\n🎉 Connection successful!",
        "connected": True
    }

if __name__ == "__main__":
    print("="*60)
    print("🌐 CORS ENABLED BACKEND")
    print("📍 http://localhost:8000")
    print("🔗 Frontend: http://localhost:3000")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
