import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime
import tempfile
import PyPDF2
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

# SİZİN OPENAI API KEY'İNİZ
os.environ["OPENAI_API_KEY"] = "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"

app = FastAPI(title="PDF AI Assistant Pro")

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

class ChatResponse(BaseModel):
    answer: str
    question: str
    pdfId: str
    timestamp: str
    confidence: float

# AI Model - GPT-4 Turbo
try:
    llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.3,
        max_tokens=1500,
        timeout=30
    )
    print("✅ OpenAI model initialized successfully")
except Exception as e:
    print(f"❌ OpenAI init error: {e}")
    llm = None

# PDF'den metin çıkarma
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text[:10000]  # İlk 10k karakter
    except Exception as e:
        return f"PDF okuma hatası: {str(e)}"

# Bellekte PDF depolama
pdf_storage = {}

@app.get("/api/health")
async def health_check():
    ai_status = "connected" if llm else "disconnected"
    return {
        "status": "healthy",
        "service": "PDF AI Pro",
        "ai_status": ai_status,
        "model": "gpt-4-turbo" if llm else "none",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Sadece PDF dosyaları kabul edilir")
        
        print(f"📤 Uploading: {file.filename}")
        
        # PDF'i geçici dosyaya kaydet
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # PDF'den metin çıkar
        with open(tmp_path, 'rb') as f:
            pdf_text = extract_text_from_pdf(f)
        
        # Depola
        file_id = f"pdf_{int(datetime.now().timestamp())}"
        pdf_storage[file_id] = {
            "filename": file.filename,
            "text": pdf_text,
            "upload_time": datetime.now().isoformat(),
            "text_length": len(pdf_text),
            "pages": pdf_text.count('\f') + 1
        }
        
        # Geçici dosyayı sil
        import os
        os.unlink(tmp_path)
        
        print(f"✅ PDF uploaded: {file.filename}, Text: {len(pdf_text)} chars")
        
        return {
            "id": file_id,
            "filename": file.filename,
            "size": len(content),
            "text_preview": pdf_text[:300] + "..." if len(pdf_text) > 300 else pdf_text,
            "pages": pdf_storage[file_id]["pages"],
            "message": "PDF başarıyla yüklendi ve AI için hazırlandı",
            "ai_ready": llm is not None
        }
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(500, f"Yükleme hatası: {str(e)}")

@app.post("/api/chat")
async def chat_with_pdf(request: ChatRequest):
    try:
        print(f"🤖 AI Question: {request.question[:50]}... (PDF: {request.pdfId})")
        
        # PDF içeriğini al
        pdf_data = pdf_storage.get(request.pdfId)
        
        if not pdf_data:
            # Demo PDF içeriği
            pdf_content = """
            GİZLİ PROJE X RAPORU
            Hazırlayan: Dr. Ahmet Yılmaz - Araştırma Direktörü
            Yardımcı Yazar: Prof. Dr. Mehmet Kaya
            Tarih: 15 Ocak 2024
            Şifre: Mavi Kelebek
            Proje Yöneticisi: Kediler Alemi Başkanı Tekir
            Bütçe: 1.000.000 TL
            Durum: Aktif
            Süre: 12 Ay
            
            ÖZET:
            Bu rapor, Proje X'in gelişim aşamalarını ve başarı metriklerini detaylandırmaktadır.
            Proje kapsamında yapay zeka entegrasyonu, PDF analiz sistemleri ve doğal dil işleme
            teknolojileri incelenmiştir.
            
            BÖLÜMLER:
            1. Giriş ve Amaç
            2. Metodoloji
            3. Bulgular
            4. Sonuç ve Öneriler
            
            İLETİŞİM:
            E-posta: projex@ornek.com
            Telefon: +90 555 123 4567
            """
            has_real_pdf = False
        else:
            pdf_content = pdf_data["text"]
            has_real_pdf = True
            print(f"📄 Real PDF content: {len(pdf_content)} chars, {pdf_data['pages']} pages")
        
        # Eğer OpenAI bağlantısı yoksa, yerel analiz
        if not llm:
            print("⚠️ OpenAI not available, using fallback")
            
            # Basit analiz
            if 'yazar' in request.question.lower() or 'kim yazdı' in request.question.lower():
                answer = "📝 YAZAR ANALİZİ:\nPDF içeriğine göre bu belgeyi 'Dr. Ahmet Yılmaz - Araştırma Direktörü' hazırlamıştır."
            elif 'şifre' in request.question.lower():
                answer = "🔐 ŞİFRE ANALİZİ:\nBelgede geçen şifre: 'Mavi Kelebek'"
            elif 'ne hakkında' in request.question.lower():
                answer = "📄 KONU ANALİZİ:\nBu PDF, Proje X'in yapay zeka entegrasyonu ve PDF analiz sistemleri hakkında bir rapordur."
            elif 'iletişim' in request.question.lower() or 'e-posta' in request.question.lower():
                answer = "📞 İLETİŞİM BİLGİLERİ:\nE-posta: projex@ornek.com\nTelefon: +90 555 123 4567"
            else:
                answer = f"🤖 PDF ANALİZİ:\n\n'{request.question}' sorusu için PDF incelendi.\n\nPDF İçeriği Özeti:\n{pdf_content[:500]}..."
            
            return {
                "answer": answer + "\n\n(Not: OpenAI bağlantısı yok, yerel analiz)",
                "question": request.question,
                "pdfId": request.pdfId,
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.7,
                "source": "Local Analyzer",
                "has_real_pdf": has_real_pdf
            }
        
        # AI'ya gönderilecek sistem mesajı
        system_message = SystemMessage(content=f"""
        Sen bir profesyonel PDF analiz uzmanısın. Kullanıcının yüklediği PDF dosyasının içeriği şudur:

        {pdf_content[:6000]}

        ÖNEMLİ KURALLAR:
        1. SADECE ve SADECE yukarıdaki PDF içeriğine dayanarak cevap ver
        2. PDF'de olmayan hiçbir şeyi uydurma
        3. Eğer PDF'de bir bilgi yoksa, "Bu bilgi bu PDF'de bulunmuyor" de
        4. PDF'den direkt alıntılar yap (tırnak içinde)
        5. Türkçe cevap ver, açık ve net ol
        6. Eğer soru PDF ile ilgili değilse, "Bu soru yüklediğiniz PDF ile ilgili değil" de
        7. Yazar, tarih, şifre, iletişim gibi spesifik bilgileri varsa mutlaka belirt

        PDF ÖZELLİKLERİ:
        - Dosya: {pdf_data['filename'] if has_real_pdf else 'Demo PDF'}
        - Karakter: {len(pdf_content)}
        - Sayfa: {pdf_data['pages'] if has_real_pdf else 'Bilinmiyor'}
        """)
        
        # Kullanıcı mesajı
        human_message = HumanMessage(content=request.question)
        
        # AI'ya sor
        print("⏳ OpenAI'ye soruluyor...")
        response = llm.invoke([system_message, human_message])
        
        ai_answer = response.content
        
        print(f"✅ OpenAI cevap verdi: {len(ai_answer)} karakter")
        
        return {
            "answer": ai_answer,
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.95,
            "source": "OpenAI GPT-4 Turbo",
            "has_real_pdf": has_real_pdf,
            "response_length": len(ai_answer)
        }
        
    except Exception as e:
        print(f"❌ AI processing error: {e}")
        # Fallback cevap
        return {
            "answer": f"""⚠️ AI İŞLEME HATASI

Hata: {str(e)}

PDF İÇERİĞİ ÖZETİ:
{pdf_content[:500] if 'pdf_content' in locals() else 'PDF içeriği yok'}

Lütfen:
1. OpenAI API key'inizi kontrol edin
2. İnternet bağlantınızı kontrol edin
3. PDF'in metin içerdiğinden emin olun

Geçici çözüm: Sorunuzu farklı şekilde sormayı deneyin.""",
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.1,
            "source": "Error Handler"
        }

@app.get("/api/pdfs")
async def list_pdfs():
    """Yüklenen PDF'leri listele"""
    return {
        "count": len(pdf_storage),
        "pdfs": [
            {
                "id": pid,
                "filename": data["filename"],
                "upload_time": data["upload_time"],
                "size": data["text_length"]
            }
            for pid, data in pdf_storage.items()
        ]
    }

if __name__ == "__main__":
    print("🚀 PDF AI ASSISTANT PRO")
    print("📍 http://localhost:8000")
    print("🤖 OpenAI GPT-4 Turbo entegre")
    print(f"🔑 API Key: {'✅ Var' if os.environ.get('OPENAI_API_KEY') else '❌ Yok'}")
    print("═" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
