import os
os.environ["OPENAI_API_KEY"] = "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"

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import tempfile
import PyPDF2
from openai import OpenAI
import json

print("🚀 OPENAI BACKEND BAŞLATILIYOR...")
print("🔑 API Key kontrol ediliyor...")

# OpenAI istemcisi
try:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    # Test et
    test_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Merhaba"}],
        max_tokens=10
    )
    print("✅ OpenAI bağlantısı BAŞARILI!")
    print(f"🤖 Model: gpt-3.5-turbo")
    openai_connected = True
except Exception as e:
    print(f"❌ OpenAI bağlantı hatası: {e}")
    openai_connected = False

app = FastAPI(title="PDF AI Assistant - OpenAI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    pdfId: str
    question: str

# PDF'den metin çıkarma
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"Sayfa {i+1}:\n{page_text}\n\n"
        return text[:12000]  # İlk 12k karakter
    except Exception as e:
        return f"PDF okuma hatası: {str(e)}"

# Bellekte PDF depolama
pdf_storage = {}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "PDF AI - OpenAI",
        "openai_connected": openai_connected,
        "model": "gpt-3.5-turbo",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Sadece PDF dosyaları kabul edilir")
        
        print(f"📤 Yükleniyor: {file.filename}")
        
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        with open(tmp_path, 'rb') as f:
            pdf_text = extract_text_from_pdf(f)
        
        file_id = f"pdf_{int(datetime.now().timestamp())}"
        pdf_storage[file_id] = {
            "filename": file.filename,
            "text": pdf_text,
            "upload_time": datetime.now().isoformat(),
            "size": len(content),
            "pages": pdf_text.count('Sayfa')
        }
        
        import os
        os.unlink(tmp_path)
        
        print(f"✅ PDF yüklendi: {file.filename}, {len(pdf_text)} karakter, {pdf_storage[file_id]['pages']} sayfa")
        
        return {
            "id": file_id,
            "filename": file.filename,
            "size": len(content),
            "pages": pdf_storage[file_id]["pages"],
            "message": "PDF OpenAI için hazır",
            "openai_ready": openai_connected
        }
        
    except Exception as e:
        print(f"❌ Yükleme hatası: {e}")
        raise HTTPException(500, f"Yükleme hatası: {str(e)}")

@app.post("/api/chat")
async def chat_with_pdf(request: ChatRequest):
    try:
        print(f"\n🤖 SORU: {request.question}")
        print(f"📄 PDF ID: {request.pdfId}")
        
        pdf_data = pdf_storage.get(request.pdfId)
        
        if pdf_data:
            pdf_content = pdf_data["text"]
            print(f"📊 Gerçek PDF: {pdf_data['filename']}, {len(pdf_content)} karakter")
        else:
            pdf_content = """
            DEMO PDF İÇERİĞİ:
            Başlık: Örnek Teknik Rapor
            Yazar: Dr. Ahmet Tekin
            Tarih: 31 Ocak 2024
            Departman: Yazılım Geliştirme
            
            İÇERİK:
            Bu belge örnek bir PDF içeriğidir. OpenAI ile entegre 
            PDF analiz sistemi demo amaçlıdır.
            
            PROJE BİLGİLERİ:
            - Proje Adı: PDF AI Assistant
            - Versiyon: 2.0
            - Teknoloji: FastAPI, React, OpenAI GPT
            - Durum: Aktif Geliştirme
            
            İLETİŞİM:
            - E-posta: info@ornek.com
            - Telefon: +90 555 123 4567
            
            NOT: Gerçek bir PDF yüklediğinizde, bu içerik yerine 
            yüklediğiniz PDF'in içeriği kullanılacaktır.
            """
            print("⚠️ Demo PDF içeriği kullanılıyor")
        
        if not openai_connected:
            return {
                "answer": "❌ OpenAI bağlantısı yok. Lütfen API key'inizi kontrol edin.",
                "question": request.question,
                "pdfId": request.pdfId,
                "timestamp": datetime.now().isoformat(),
                "source": "Error"
            }
        
        # OpenAI'ye sor
        print("⏳ OpenAI GPT'ye soruluyor...")
        
        system_prompt = f"""
        Sen bir PDF analiz uzmanısın. Aşağıda bir PDF'in içeriği var:

        {pdf_content[:8000]}

        KURALLAR:
        1. SADECE bu PDF içeriğine dayanarak cevap ver
        2. PDF'de olmayan hiçbir şeyi uydurma
        3. Eğer PDF'de bir bilgi yoksa, "Bu bilgi PDF'de bulunmuyor" de
        4. PDF'den direkt alıntılar yap
        5. Türkçe cevap ver
        6. Detaylı, açıklayıcı ve profesyonel ol
        7. Yazar, tarih, iletişim, şifre gibi spesifik bilgileri belirt

        PDF: {pdf_data['filename'] if pdf_data else 'Demo PDF'}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.question}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        ai_answer = response.choices[0].message.content
        
        print(f"✅ OpenAI cevap verdi: {len(ai_answer)} karakter")
        
        return {
            "answer": ai_answer,
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.95,
            "source": "OpenAI GPT-3.5-Turbo",
            "tokens": response.usage.total_tokens if hasattr(response, 'usage') else None
        }
        
    except Exception as e:
        print(f"❌ OpenAI hatası: {e}")
        return {
            "answer": f"❌ AI İŞLEME HATASI:\n\n{str(e)}\n\nPDF içeriği: {pdf_content[:500] if 'pdf_content' in locals() else 'Yok'}",
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "source": "Error"
        }

@app.get("/api/test-openai")
async def test_openai():
    """OpenAI bağlantı testi"""
    try:
        test = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Merhaba, OpenAI çalışıyor mu?"}],
            max_tokens=50
        )
        return {
            "success": True,
            "response": test.choices[0].message.content,
            "model": "gpt-3.5-turbo"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("📍 http://localhost:8000")
    print("═" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
