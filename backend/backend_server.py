from fastapi import FastAPI
import uvicorn

# Basit app
app = FastAPI()

@app.get("/")
def root():
    return {"status": "RUNNING", "message": "Backend is ALIVE!"}

@app.post("/api/upload")
def upload():
    return {"id": "test-id", "filename": "test.pdf", "uploaded": True}

@app.post("/api/chat/{pdf_id}")
def chat(pdf_id: str, question: str):
    return {"answer": f"Backend response for {pdf_id}: {question}"}

# BAŞLAT
if __name__ == "__main__":
    print("="*50)
    print("🚀 BACKEND SERVER STARTING ON PORT 8000")
    print("="*50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
