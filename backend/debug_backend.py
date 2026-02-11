from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "debug", "message": "Backend debugging"}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    print(f"📤 Received upload: {file.filename}, {file.content_type}")
    return {
        "id": "debug-id",
        "filename": file.filename,
        "status": "success",
        "debug": True
    }

@app.post("/api/chat/{pdf_id}")
async def chat(pdf_id: str, question: str = Form(...)):
    print(f"🤔 Chat request - PDF: {pdf_id}, Q: {question}")
    return {
        "answer": f"Debug response for {pdf_id}: {question}",
        "debug": True
    }

if __name__ == "__main__":
    print("🐛 DEBUG BACKEND STARTING...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
