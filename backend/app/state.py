# app/state.py
"""
HYBRID STATE MANAGEMENT (Migration için)
Eski RAM state + Yeni Database entegrasyonu
"""
import json
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)


# ========== MEVCUT RAM STATE (Backward Compatibility) ==========
# Bu kısım eski kodun çalışması için kalacak

UPLOADED_PDFS = []  # Eski format: List[Dict]
PDF_VECTOR_DBS = {}  # Eski format: Dict[str, Any]
GLOBAL_VECTOR_DB = None  # Tüm PDF'lerin birleşmiş hali


def update_global_vector_db():
    """Eski fonksiyon - tüm PDF'leri birleştir (Migration için tutuyoruz)"""
    global GLOBAL_VECTOR_DB
    # Eski mantık
    if PDF_VECTOR_DBS:
        # Basit birleştirme (gerçek projede FAISS merge kullan)
        GLOBAL_VECTOR_DB = list(PDF_VECTOR_DBS.values())
    else:
        GLOBAL_VECTOR_DB = None


def add_pdf_vector_db(pdf_id: str, vector_db: Any):
    """Eski fonksiyon - PDF vektör DB ekle"""
    PDF_VECTOR_DBS[pdf_id] = vector_db
    update_global_vector_db()


def get_pdf_vector_db(pdf_id: str) -> Optional[Any]:
    """Eski fonksiyon - PDF vektör DB getir"""
    return PDF_VECTOR_DBS.get(pdf_id)


def get_global_vector_db():
    """Eski fonksiyon - Global vektör DB getir"""
    return GLOBAL_VECTOR_DB


# ========== YENİ HYBRID STATE SINIFI ==========

class HybridState:
    """
    Yeni state yönetimi: RAM cache + Database source of truth
    Migration sürecinde eski kodla uyumlu
    """
    
    def __init__(self):
        # RAM cache (performans için)
        self.pdf_cache: Dict[str, Dict] = {}
        self.vector_cache: Dict[str, Any] = {}
        
        # Services (lazy loading)
        self._pdf_service = None
        self._db_service = None
        
        logger.info("HybridState initialized - Migration mode active")
    
    @property
    def pdf_service(self):
        """Lazy loading for PDF service"""
        if self._pdf_service is None:
            from app.services.pdf_service import pdf_service
            self._pdf_service = pdf_service
        return self._pdf_service
    
    @property
    def db_service(self):
        """Lazy loading for Database service"""
        if self._db_service is None:
            from app.services.database_service import db_service
            self._db_service = db_service
        return self._db_service
    
    # ========== PDF YÖNETİMİ ==========
    
    async def upload_pdf(self, file, user_id: str = "system") -> Dict[str, Any]:
        """
        PDF yükle (Yeni yöntem)
        Hem database'e kaydeder hem de RAM cache'ler
        """
        try:
            # 1. PDF Service ile yükle (database'e kaydeder)
            result = await self.pdf_service.upload_pdf(file, user_id)
            
            if result.get("success"):
                pdf_id = result.get("pdf_id")
                
                # 2. RAM cache'i güncelle
                pdf_info = self.pdf_service.get_pdf_info(pdf_id)
                if pdf_info:
                    self.pdf_cache[pdf_id] = pdf_info
                
                # 3. Eski state'i de güncelle (backward compatibility)
                global UPLOADED_PDFS, PDF_VECTOR_DBS
                
                # Eski UPLOADED_PDFS'e ekle
                if pdf_info:
                    UPLOADED_PDFS.append({
                        "id": pdf_id,
                        "filename": pdf_info.get("filename"),
                        "user_id": user_id,
                        "page_count": pdf_info.get("page_count", 0),
                        "chunk_count": pdf_info.get("chunk_count", 0)
                    })
                
                # Vektör DB'yi cache'le
                vector_db = self.pdf_service.load_vector_store(pdf_id)
                if vector_db:
                    self.vector_cache[pdf_id] = vector_db
                    PDF_VECTOR_DBS[pdf_id] = vector_db
                    update_global_vector_db()
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid upload error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_pdfs(self, user_id: str) -> List[Dict]:
        """
        Kullanıcının PDF'lerini getir
        Önce cache, sonra database
        """
        try:
            # Önce cache'den getir
            cached_pdfs = [
                pdf for pdf in self.pdf_cache.values() 
                if pdf.get("user_id") == user_id
            ]
            
            if cached_pdfs:
                return cached_pdfs
            
            # Cache yoksa database'den getir
            db_pdfs = self.pdf_service.list_user_pdfs(user_id)
            
            # Cache'i güncelle
            for pdf in db_pdfs:
                self.pdf_cache[pdf["id"]] = pdf
            
            return db_pdfs
            
        except Exception as e:
            logger.error(f"Get user PDFs error: {e}")
            return []
    
    def get_pdf(self, pdf_id: str) -> Optional[Dict]:
        """PDF bilgilerini getir"""
        try:
            # Önce cache
            if pdf_id in self.pdf_cache:
                return self.pdf_cache[pdf_id]
            
            # Sonra database
            pdf_info = self.pdf_service.get_pdf_info(pdf_id)
            if pdf_info:
                self.pdf_cache[pdf_id] = pdf_info
            
            return pdf_info
            
        except Exception as e:
            logger.error(f"Get PDF error: {e}")
            return None
    
    def get_vector_store(self, pdf_id: str) -> Optional[Any]:
        """PDF'in vektör store'unu getir"""
        try:
            # Önce cache
            if pdf_id in self.vector_cache:
                return self.vector_cache[pdf_id]
            
            # Sonra diskten yükle
            vector_db = self.pdf_service.load_vector_store(pdf_id)
            if vector_db:
                self.vector_cache[pdf_id] = vector_db
            
            return vector_db
            
        except Exception as e:
            logger.error(f"Get vector store error: {e}")
            return None
    
    def delete_pdf(self, pdf_id: str, user_id: str = None) -> bool:
        """PDF'i sil"""
        try:
            # 1. Database'den sil
            success = self.pdf_service.delete_pdf(pdf_id, user_id)
            
            if success:
                # 2. Cache'leri temizle
                if pdf_id in self.pdf_cache:
                    del self.pdf_cache[pdf_id]
                
                if pdf_id in self.vector_cache:
                    del self.vector_cache[pdf_id]
                
                # 3. Eski state'i temizle (backward compatibility)
                global UPLOADED_PDFS, PDF_VECTOR_DBS
                UPLOADED_PDFS = [
                    pdf for pdf in UPLOADED_PDFS 
                    if pdf.get("id") != pdf_id
                ]
                
                if pdf_id in PDF_VECTOR_DBS:
                    del PDF_VECTOR_DBS[pdf_id]
                    update_global_vector_db()
            
            return success
            
        except Exception as e:
            logger.error(f"Delete PDF error: {e}")
            return False
    
    # ========== SİSTEM YÖNETİMİ ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """Sistem istatistiklerini getir"""
        try:
            # Database stats
            db_stats = self.db_service.get_system_stats()
            
            # Cache stats
            cache_stats = {
                "pdf_cache_size": len(self.pdf_cache),
                "vector_cache_size": len(self.vector_cache),
                "legacy_pdfs_count": len(UPLOADED_PDFS),
                "legacy_vector_dbs_count": len(PDF_VECTOR_DBS)
            }
            
            return {
                **db_stats,
                **cache_stats,
                "migration_mode": True,
                "state_version": "hybrid_1.0"
            }
            
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {"error": str(e)}
    
    def clear_cache(self):
        """Cache'i temizle"""
        self.pdf_cache.clear()
        self.vector_cache.clear()
        logger.info("HybridState cache cleared")
    
    def migrate_legacy_data(self):
        """
        Eski RAM'deki verileri database'e taşı (Migration fonksiyonu)
        Bu fonksiyonu bir kere çalıştırman yeterli
        """
        try:
            logger.info("Starting legacy data migration...")
            
            # Bu kısımda eski UPLOADED_PDFS'deki verileri
            # database'e taşıyacak kod olacak
            # Şimdilik sadece log atıyoruz
            
            logger.info(f"Legacy PDFs to migrate: {len(UPLOADED_PDFS)}")
            logger.info("Migration function ready - implement as needed")
            
            return {
                "status": "migration_ready",
                "legacy_items": len(UPLOADED_PDFS),
                "note": "Manual migration required"
            }
            
        except Exception as e:
            logger.error(f"Migration error: {e}")
            return {"error": str(e)}


# ========== GLOBAL INSTANCES ==========

# Yeni hybrid state
hybrid_state = HybridState()

# Backward compatibility için alias'lar
# Eski kodlar hala bu isimleri kullanabilir
app_state = hybrid_state