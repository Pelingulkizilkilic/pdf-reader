from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Question(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "alive", "test": "works"}

@app.post("/api/chat/{pdf_id}")
def chat(pdf_id: str, q: Question):
    return {
        "answer": f"PowerShell test SUCCESS! PDF: {pdf_id}, Q: {q.question}",
        "status": "working"
    }

if __name__ == "__main__":
    print("✅ SIMPLE BACKEND STARTING...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
