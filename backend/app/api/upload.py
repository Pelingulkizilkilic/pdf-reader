# app/api/upload.py
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.auth import get_current_user
from app.state import hybrid_state  # YENİ: hybrid_state kullan

router = APIRouter()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """PDF yükleme endpoint'i (GÜNCELLENMİŞ)"""
    try:
        # Kullanıcı bilgisi
        user_id = str(current_user.get("id", "system"))
        
        # Dosya kontrolü
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sadece PDF dosyaları yüklenebilir"
            )
        
        # Hybrid state ile yükle
        result = await hybrid_state.upload_pdf(file, user_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "PDF yükleme hatası")
            )
        
        return {
            "message": "PDF başarıyla yüklendi",
            "pdf_id": result.get("pdf_id"),
            "filename": file.filename,
            "database_id": result.get("database_id"),
            "chunks": result.get("chunks", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF yükleme hatası: {str(e)}"
        )


@router.get("/pdfs")
async def get_user_pdfs(
    current_user: dict = Depends(get_current_user)
):
    """Kullanıcının PDF'lerini getir (GÜNCELLENMİŞ)"""
    user_id = str(current_user.get("id", "system"))
    
    # Hybrid state'ten PDF'leri getir
    pdfs = hybrid_state.get_user_pdfs(user_id)
    
    return {
        "user_id": user_id,
        "pdf_count": len(pdfs),
        "pdfs": pdfs
    }


@router.delete("/pdf/{pdf_id}")
async def delete_pdf(
    pdf_id: str,
    current_user: dict = Depends(get_current_user)
):
    """PDF'i sil (GÜNCELLENMİŞ)"""
    user_id = str(current_user.get("id", "system"))
    
    # Önce PDF'in kullanıcıya ait olduğunu kontrol et
    pdf_info = hybrid_state.get_pdf(pdf_id)
    if not pdf_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF bulunamadı"
        )
    
    # Silme işlemi
    success = hybrid_state.delete_pdf(pdf_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF silinemedi"
        )
    
    return {
        "message": "PDF başarıyla silindi",
        "pdf_id": pdf_id
    }


@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(get_current_user)
):
    """Sistem istatistiklerini getir (YENİ)"""
    # Sadece admin için yapabilirsin, şimdilik herkes görebilir
    stats = hybrid_state.get_stats()
    
    return {
        "system_stats": stats,
        "user_id": current_user.get("id")
    }