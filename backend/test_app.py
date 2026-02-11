from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# KÖK ENDPOINT EKLE
@app.get("/")
def root():
    return {"message": "PDF AI Backend", "status": "running", "version": "1.0"}

# PDF upload endpoint
@app.post("/api/upload")
async def upload_pdf():
    return {"id": "test-id", "filename": "test.pdf", "status": "uploaded"}

# Chat endpoint
@app.post("/api/chat/{pdf_id}")
async def chat(pdf_id: str, question: str):
    return {"answer": f"Answer for {pdf_id}: {question}", "pdf_id": pdf_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
