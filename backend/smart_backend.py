from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import tempfile
import PyPDF2
import json
import re

app = FastAPI(title="PDF AI Assistant - WORKING VERSION")

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

# PDF'den metin çıkarma (gelişmiş)
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"--- Sayfa {i+1} ---\n{page_text}\n\n"
        return text
    except Exception as e:
        print(f"PDF okuma hatası: {e}")
        return ""

# Akıllı PDF analizi (OpenAI olmadan)
def analyze_pdf_intelligently(pdf_text, question):
    q_lower = question.lower()
    text_lower = pdf_text.lower()
    
    print(f"Analiz: '{question}' - PDF: {len(pdf_text)} karakter")
    
    # 1. Yazar/oluşturucu bulma
    if any(word in q_lower for word in ['yazar', 'kim yazdı', 'hazırlayan', 'oluşturan', 'yazan']):
        # Yazar pattern'leri
        patterns = [
            r'(yazar|hazırlayan|oluşturan|yazan)[\s:]+([^\n]+)',
            r'([A-Z][a-z]+ [A-Z][a-z]+)(?=.*(rapor|doküman|belge))',
            r'(Dr\.|Prof\.|Doç\.) ([A-Z][a-z]+ [A-Z][a-z]+)',
            r'© (\d{4}) ([A-Za-z ]+)',
            r'prepared by:? ([^\n]+)',
            r'author:? ([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                groups = [g for g in match.groups() if g]
                return f"📝 **YAZAR BİLGİSİ:**\n\nBu PDF'yi `{groups[-1]}` hazırlamıştır.\n\n*(PDF'deki orijinal metin: \"{match.group(0)}\")*"
        
        # E-posta veya şirket adı ara
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', pdf_text)
        if email_match:
            return f"📧 **İLETİŞİM/YAZAR:**\n\nYazarın e-posta adresi: `{email_match.group(0)}`\n\n*(Bu e-posta adresi PDF'de bulunuyor)*"
        
        return "ℹ️ **YAZAR BİLGİSİ:**\n\nBu PDF'de açık bir yazar/hazırlayan bilgisi bulunamadı. Belge anonim veya şirket raporu olabilir."
    
    # 2. Şifre/parola bulma
    elif any(word in q_lower for word in ['şifre', 'parola', 'password', 'güvenlik']):
        password_patterns = [
            r'(şifre|parola|password)[\s:]+([^\n]+)',
            r'key:? ([^\n]+)',
            r'code:? ([^\n]+)',
            r'[\w-]{6,20}(?=.*(şifre|parola|password))'
        ]
        
        for pattern in password_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return f"🔐 **ŞİFRE BİLGİSİ:**\n\nPDF'de geçen şifre/anahtar: `{match.group(0)}`\n\n*(Direkt PDF içeriğinden alınmıştır)*"
        
        return "🔒 **ŞİFRE BİLGİSİ:**\n\nBu PDF'de açık bir şifre/parola bilgisi bulunmuyor."
    
    # 3. Tarih bilgisi
    elif any(word in q_lower for word in ['tarih', 'ne zaman', 'date', 'when']):
        date_patterns = [
            r'\d{1,2}[\./]\d{1,2}[\./]\d{2,4}',
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'\d{1,2} [A-Za-z]+ \d{4}',
            r'(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)[\s\w,]* \d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, pdf_text, re.IGNORECASE))
        
        if dates:
            return f"📅 **TARİH BİLGİLERİ:**\n\nPDF'de geçen tarihler:\n" + "\n".join([f"• `{d}`" for d in set(dates[:5])])
        
        return "📅 **TARİH BİLGİSİ:**\n\nPDF'de belirgin tarih bilgisi bulunamadı."
    
    # 4. İletişim bilgileri
    elif any(word in q_lower for word in ['iletişim', 'contact', 'e-posta', 'email', 'telefon', 'phone']):
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        emails = re.findall(email_pattern, pdf_text)
        phones = re.findall(phone_pattern, pdf_text)
        
        response = "📞 **İLETİŞİM BİLGİLERİ:**\n\n"
        
        if emails:
            response += "**E-posta Adresleri:**\n" + "\n".join([f"• `{email}`" for email in set(emails[:3])]) + "\n\n"
        
        if phones:
            response += "**Telefon Numaraları:**\n" + "\n".join([f"• `{phone}`" for phone in set(phones[:3])]) + "\n\n"
        
        if not emails and not phones:
            response += "PDF'de açık iletişim bilgisi (e-posta/telefon) bulunamadı.\n"
        
        return response
    
    # 5. Ne hakkında / konu
    elif 'ne hakkında' in q_lower or 'konu' in q_lower or 'içerik' in q_lower:
        # İlk 3 satırı ve son 3 satırı al
        lines = pdf_text.split('\n')
        relevant_lines = lines[:5] + lines[-5:] if len(lines) > 10 else lines
        
        # Anahtar kelimeleri bul
        keywords = ['rapor', 'proje', 'analiz', 'çalışma', 'araştırma', 'doküman', 'sözleşme', 'fatura', 'teklif', 'sunum']
        found_keywords = [kw for kw in keywords if kw in text_lower]
        
        response = "📄 **PDF İÇERİK ANALİZİ:**\n\n"
        
        if found_keywords:
            response += f"**Ana Konular:** {', '.join(found_keywords)}\n\n"
        
        response += "**İçerik Önizleme:**\n"
        for line in relevant_lines:
            if line.strip() and len(line.strip()) > 20:
                response += f"• {line[:100]}...\n"
        
        # Sayfa/karakter bilgisi
        char_count = len(pdf_text)
        page_count = pdf_text.count('--- Sayfa')
        response += f"\n**Teknik Detaylar:**\n• Karakter sayısı: {char_count}\n• Tahmini sayfa: {page_count if page_count > 0 else '1'}"
        
        return response
    
    # 6. Genel sorular için
    else:
        # PDF'de soruyla ilgili kelimeleri ara
        words = q_lower.split()
        found_lines = []
        
        for word in words:
            if len(word) > 3:  # Kısa kelimeleri atla
                for line in pdf_text.split('\n'):
                    if word in line.lower() and len(line) > 20:
                        found_lines.append(line[:150])
                        if len(found_lines) >= 3:
                            break
        
        if found_lines:
            response = f"🔍 **'{question}' SORUSU İÇİN PDF ANALİZİ:**\n\n"
            response += "PDF'de ilgili bulunan bölümler:\n\n"
            for i, line in enumerate(set(found_lines[:3]), 1):
                response += f"{i}. `{line}...`\n\n"
            response += "*(Yukarıdaki metinler doğrudan PDF'den alınmıştır)*"
        else:
            # PDF özeti göster
            first_part = pdf_text[:500].replace('\n', ' ')
            if len(pdf_text) > 500:
                first_part += "..."
            
            response = f"🤖 **PDF GENEL ANALİZİ:**\n\n"
            response += f"**Soru:** \"{question}\"\n\n"
            response += f"**PDF Özeti:**\n{first_part}\n\n"
            response += f"**Analiz:** Sorunuz için PDF'de spesifik bilgi bulunamadı. Yukarıda PDF'nin başlangıç kısmı verilmiştir."
        
        return response

# Bellekte PDF depolama
pdf_storage = {}

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "PDF AI Assistant Pro",
        "ai": "Advanced Rule-Based",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0"
    }

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Sadece PDF dosyaları kabul edilir")
        
        print(f"📤 Yükleniyor: {file.filename}")
        
        # PDF'i oku
        content = await file.read()
        
        # Geçici dosya
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Metni çıkar
        with open(tmp_path, 'rb') as f:
            pdf_text = extract_text_from_pdf(f)
        
        if not pdf_text or len(pdf_text.strip()) < 10:
            pdf_text = "⚠️ PDF'den metin çıkarılamadı veya metin çok kısa. Bu bir resim PDF'i olabilir."
        
        # Depola
        file_id = f"pdf_{int(datetime.now().timestamp())}"
        pdf_storage[file_id] = {
            "filename": file.filename,
            "text": pdf_text,
            "upload_time": datetime.now().isoformat(),
            "size": len(content)
        }
        
        # Temizle
        import os
        os.unlink(tmp_path)
        
        print(f"✅ Başarıyla yüklendi: {file.filename} ({len(pdf_text)} karakter)")
        
        return {
            "id": file_id,
            "filename": file.filename,
            "size": len(content),
            "text_preview": pdf_text[:200] + "..." if len(pdf_text) > 200 else pdf_text,
            "message": "PDF başarıyla yüklendi ve analiz için hazır",
            "has_text": len(pdf_text.strip()) > 10
        }
        
    except Exception as e:
        print(f"❌ Yükleme hatası: {e}")
        raise HTTPException(500, f"Yükleme hatası: {str(e)}")

@app.post("/api/chat")
async def chat_with_pdf(request: ChatRequest):
    try:
        print(f"💬 Soru: {request.question} (PDF: {request.pdfId})")
        
        # PDF içeriğini al
        pdf_data = pdf_storage.get(request.pdfId)
        
        if pdf_data and pdf_data["text"]:
            pdf_text = pdf_data["text"]
            has_real_pdf = True
            print(f"📄 Gerçek PDF: {len(pdf_text)} karakter")
        else:
            # Demo PDF
            pdf_text = """TEKNİK RAPOR: PDF ANALİZ SİSTEMİ

Hazırlayan: Yapay Zeka Araştırma Ekibi
Tarih: 31 Ocak 2024
Rapor No: AI-2024-001

ÖZET:
Bu rapor, geliştirilen PDF analiz sisteminin teknik detaylarını içermektedir.
Sistem kullanıcıların yüklediği PDF dosyalarını işleyerek akıllı sorgulara
yanıt verebilmektedir.

TEKNİK ÖZELLİKLER:
- Desteklenen format: PDF
- Metin çıkarma: PyPDF2 kütüphanesi
- Analiz motoru: Kural-tabanlı AI
- Yanıt süresi: < 2 saniye

İLETİŞİM:
E-posta: ai-team@ornek.com
Telefon: +90 212 555 01 02"""
            has_real_pdf = False
            print("⚠️ Demo PDF kullanılıyor")
        
        # Akıllı analiz
        answer = analyze_pdf_intelligently(pdf_text, request.question)
        
        print(f"✅ Cevap hazır: {len(answer)} karakter")
        
        return {
            "answer": answer,
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.85,
            "source": "Advanced PDF Analyzer",
            "has_real_pdf": has_real_pdf,
            "pdf_filename": pdf_data["filename"] if has_real_pdf else "Demo PDF"
        }
        
    except Exception as e:
        print(f"❌ Analiz hatası: {e}")
        return {
            "answer": f"❌ SİSTEM HATASI\n\nHata: {str(e)}\n\nLütfen tekrar deneyin veya farklı bir PDF yükleyin.",
            "question": request.question,
            "pdfId": request.pdfId,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "source": "Error"
        }

if __name__ == "__main__":
    print("🚀 PDF AI ASSISTANT PRO")
    print("📍 http://localhost:8000")
    print("🤖 Gelişmiş Kural-Tabanlı Analiz")
    print("🔧 OpenAI GEREKMEZ - %100 yerel")
    print("═" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
