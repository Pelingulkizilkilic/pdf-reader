# app/services/database_service.py
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self):
        pass
    
    # ----- HELPER FUNCTIONS -----
    
    def _get_db(self) -> Session:
        """Database session al (lazy import)"""
        from app.database.database import get_db
        return next(get_db())
    
    def _get_models(self):
        """Models modülünü al (lazy import)"""
        from app.database import models
        return models
    
    # ----- USERS -----
    
    def create_user(self, username: str, email: str, hashed_password: str) -> Optional[Any]:
        """Yeni kullanıcı oluştur"""
        try:
            db = self._get_db()
            models = self._get_models()
            
            user = models.User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Yeni kullanıcı oluşturuldu: {username}")
            return user
            
        except IntegrityError as e:
            logger.error(f"Kullanıcı oluşturma hatası (unique constraint): {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error creating user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Any]:
        """Kullanıcı adına göre kullanıcı getir"""
        try:
            db = self._get_db()
            models = self._get_models()
            return db.query(models.User).filter(models.User.username == username).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Email'e göre kullanıcı getir"""
        try:
            db = self._get_db()
            models = self._get_models()
            return db.query(models.User).filter(models.User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by email: {e}")
            return None
    
    # ----- PDF DOCUMENTS -----
    
    def create_pdf_document(self, pdf_data: Dict[str, Any]) -> Optional[Any]:
        """Yeni PDF dokümanı oluştur"""
        try:
            db = self._get_db()
            models = self._get_models()
            
            pdf = models.PDFDocument(
                id=str(uuid.uuid4()),
                user_id=pdf_data.get("user_id", "system"),
                filename=pdf_data.get("filename", ""),
                original_filename=pdf_data.get("original_filename", ""),
                file_path=pdf_data.get("file_path", ""),
                file_size=pdf_data.get("file_size", 0),
                page_count=pdf_data.get("page_count", 0),
                chunk_count=pdf_data.get("chunk_count", 0),
                vector_store_path=pdf_data.get("vector_store_path", ""),
                document_metadata=pdf_data.get("metadata", {}),  # metadata → document_metadata
                uploaded_at=datetime.utcnow()
            )
            
            db.add(pdf)
            db.commit()
            db.refresh(pdf)
            logger.info(f"PDF dokümanı oluşturuldu: {pdf.filename}")
            return pdf
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating PDF: {e}")
            return None
    
    def get_pdf_by_id(self, pdf_id: str) -> Optional[Any]:
        """ID'ye göre PDF getir"""
        try:
            db = self._get_db()
            models = self._get_models()
            return db.query(models.PDFDocument).filter(models.PDFDocument.id == pdf_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting PDF: {e}")
            return None
    
    def get_user_pdfs(self, user_id: str) -> List[Any]:
        """Kullanıcının PDF'lerini getir"""
        try:
            db = self._get_db()
            models = self._get_models()
            return db.query(models.PDFDocument).filter(
                models.PDFDocument.user_id == user_id
            ).order_by(models.PDFDocument.uploaded_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user PDFs: {e}")
            return []
    
    def get_all_pdfs(self) -> List[Any]:
        """Tüm PDF'leri getir"""
        try:
            db = self._get_db()
            models = self._get_models()
            return db.query(models.PDFDocument).order_by(
                models.PDFDocument.uploaded_at.desc()
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting all PDFs: {e}")
            return []
    
    def delete_pdf(self, pdf_id: str) -> bool:
        """PDF'i sil"""
        try:
            db = self._get_db()
            models = self._get_models()
            pdf = db.query(models.PDFDocument).filter(models.PDFDocument.id == pdf_id).first()
            if pdf:
                db.delete(pdf)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting PDF: {e}")
            return False
    
    def update_pdf_status(self, pdf_id: str, status_data: Dict[str, Any]) -> bool:
        """PDF durumunu güncelle"""
        try:
            db = self._get_db()
            models = self._get_models()
            pdf = db.query(models.PDFDocument).filter(models.PDFDocument.id == pdf_id).first()
            if pdf:
                if "processed_at" in status_data:
                    pdf.processed_at = status_data["processed_at"]
                if "vector_store_path" in status_data:
                    pdf.vector_store_path = status_data["vector_store_path"]
                
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Database error updating PDF: {e}")
            return False
    
    # ----- STATISTICS -----
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Sistem istatistiklerini getir"""
        try:
            db = self._get_db()
            models = self._get_models()
            
            total_pdfs = db.query(models.PDFDocument).count()
            total_users = db.query(models.User).count()
            
            # Son 24 saatte yüklenen PDF'ler
            twenty_four_hours_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            pdfs_today = db.query(models.PDFDocument).filter(
                models.PDFDocument.uploaded_at >= twenty_four_hours_ago
            ).count()
            
            return {
                "total_pdfs": total_pdfs,
                "total_users": total_users,
                "pdfs_today": pdfs_today,
                "database_status": "connected"
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting stats: {e}")
            return {
                "total_pdfs": 0,
                "total_users": 0,
                "pdfs_today": 0,
                "database_status": "error"
            }
    
    # ----- HEALTH CHECK -----
    
    def check_database_health(self) -> bool:
        """Database bağlantısını kontrol et"""
        try:
            db = self._get_db()
            # Basit bir query çalıştır
            db.execute("SELECT 1")
            return True
        except SQLAlchemyError:
            return False


# Global instance
db_service = DatabaseService()