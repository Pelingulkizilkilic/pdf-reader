from fastapi import UploadFile
import PyPDF2
import io
from typing import Tuple
import app.state as state
from app.rag.utils import generate_pdf_id, save_pdf_file

async def load_pdf(file: UploadFile) -> Tuple[str, str, str]:
    """PDF yükle ve metne dönüştür, PDF ID'si döndür"""
    # Dosyayı oku
    content = await file.read()
    
    # PDF ID oluştur
    pdf_id = generate_pdf_id(file.filename, content)
    
    # PDF'i diske kaydet
    filepath = save_pdf_file(content, file.filename)
    
    # PDF'den metin çıkar
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
    text = ""
    
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text() + "\n\n"
    
    # PDF bilgilerini state'e kaydet
    pdf_info = {
        "id": pdf_id,
        "filename": file.filename,
        "filepath": filepath,
        "page_count": len(pdf_reader.pages),
        "text_length": len(text)
    }
    state.UPLOADED_PDFS.append(pdf_info)
    
    return text, pdf_id, file.filename