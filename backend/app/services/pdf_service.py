import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from app.services.database_service import db_service
from app.rag.pdf_loader import load_pdf as rag_load_pdf
from app.rag.text_splitter import create_chunks_with_metadata
from app.rag.vector_store import create_faiss_index
import app.state as old_state  # Eski RAM state'i

class PDFService:
    def __init__(self):
        self.uploads_dir = "uploads"
        self.vector_stores_dir = "vector_stores"
        
        # Klasörleri oluştur
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.vector_stores_dir, exist_ok=True)
    
    async def upload_pdf(self, file, user_id: str = "system") -> Dict[str, Any]:
        """PDF yükle ve database'e kaydet"""
        try:
            # 1. PDF'i işle (eski fonksiyon)
            text, pdf_id, filename = await rag_load_pdf(file)
            
            # 2. Metni parçalara ayır
            chunks, metadata = create_chunks_with_metadata(text, pdf_id, filename)
            
            # 3. Vektör veritabanı oluştur
            vector_db = create_faiss_index(chunks, metadata)
            
            # 4. Vektör DB'yi diske kaydet
            vector_store_path = self._save_vector_store(vector_db, pdf_id)
            
            # 5. Database'e kaydet
            pdf_data = {
                "user_id": user_id,
                "filename": filename,
                "original_filename": file.filename,
                "file_path": os.path.join(self.uploads_dir, f"{pdf_id}_{filename}"),
                "file_size": len(await file.read()),
                "page_count": len(text.split('\f')),  # Basit sayfa sayısı
                "chunk_count": len(chunks),
                "vector_store_path": vector_store_path
            }
            
            # Dosyayı tekrar oku
            await file.seek(0)
            
            pdf_document = db_service.create_pdf_document(pdf_data)
            
            if pdf_document:
                # 6. Eski state'i güncelle (geçici - migration sırasında)
                old_state.add_pdf_vector_db(pdf_id, vector_db)
                
                # 7. PDF metadata'yı eski state'e ekle
                old_state.UPLOADED_PDFS.append({
                    "id": pdf_document.id,
                    "filename": filename,
                    "user_id": user_id,
                    "page_count": pdf_data["page_count"],
                    "chunk_count": len(chunks),
                    "vector_store_path": vector_store_path,
                    "uploaded_at": datetime.utcnow().isoformat()
                })
                
                return {
                    "success": True,
                    "pdf_id": pdf_document.id,
                    "filename": filename,
                    "chunks": len(chunks),
                    "database_id": pdf_document.id,
                    "message": "PDF başarıyla yüklendi ve database'e kaydedildi"
                }
            else:
                return {
                    "success": False,
                    "error": "Database'e kaydedilemedi"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_vector_store(self, vector_db, pdf_id: str) -> str:
        """Vektör veritabanını diske kaydet"""
        try:
            # FAISS index'ini kaydet
            import pickle
            
            filepath = os.path.join(self.vector_stores_dir, f"{pdf_id}.faiss")
            
            # Basit bir şekilde kaydet (gerçek projede FAISS.save_local kullan)
            with open(filepath, 'wb') as f:
                pickle.dump(vector_db, f)
            
            return filepath
        except Exception as e:
            print(f"Vector store save error: {e}")
            return ""
    
    def load_vector_store(self, pdf_id: str):
        """Vektör veritabanını diskten yükle"""
        try:
            import pickle
            
            filepath = os.path.join(self.vector_stores_dir, f"{pdf_id}.faiss")
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    return pickle.load(f)
            return None
        except Exception as e:
            print(f"Vector store load error: {e}")
            return None
    
    def get_pdf_info(self, pdf_id: str) -> Optional[Dict[str, Any]]:
        """PDF bilgilerini getir"""
        pdf = db_service.get_pdf_by_id(pdf_id)
        if pdf:
            return {
                "id": pdf.id,
                "filename": pdf.filename,
                "original_filename": pdf.original_filename,
                "file_size": pdf.file_size,
                "page_count": pdf.page_count,
                "chunk_count": pdf.chunk_count,
                "uploaded_at": pdf.uploaded_at.isoformat() if pdf.uploaded_at else None,
                "processed_at": pdf.processed_at.isoformat() if pdf.processed_at else None,
                "vector_store_path": pdf.vector_store_path
            }
        return None
    
    def list_user_pdfs(self, user_id: str) -> list:
        """Kullanıcının PDF'lerini listele"""
        pdfs = db_service.get_user_pdfs(user_id)
        return [
            {
                "id": pdf.id,
                "filename": pdf.filename,
                "page_count": pdf.page_count,
                "chunk_count": pdf.chunk_count,
                "uploaded_at": pdf.uploaded_at.isoformat() if pdf.uploaded_at else None,
                "file_size_mb": round(pdf.file_size / (1024 * 1024), 2)
            }
            for pdf in pdfs
        ]
    
    def list_all_pdfs(self) -> list:
        """Tüm PDF'leri listele"""
        pdfs = db_service.get_all_pdfs()
        return [
            {
                "id": pdf.id,
                "filename": pdf.filename,
                "user_id": pdf.user_id,
                "page_count": pdf.page_count,
                "uploaded_at": pdf.uploaded_at.isoformat() if pdf.uploaded_at else None
            }
            for pdf in pdfs
        ]
    
    def delete_pdf(self, pdf_id: str, user_id: str = None) -> bool:
        """PDF'i sil"""
        # Önce database'den sil
        success = db_service.delete_pdf(pdf_id)
        
        if success:
            # Eski state'ten de sil
            old_state.UPLOADED_PDFS = [
                pdf for pdf in old_state.UPLOADED_PDFS 
                if pdf.get("id") != pdf_id
            ]
            
            # Vektör DB'yi de sil
            if pdf_id in old_state.PDF_VECTOR_DBS:
                del old_state.PDF_VECTOR_DBS[pdf_id]
                old_state.update_global_vector_db()
            
            # Diskten de sil
            try:
                vector_path = os.path.join(self.vector_stores_dir, f"{pdf_id}.faiss")
                if os.path.exists(vector_path):
                    os.remove(vector_path)
            except:
                pass
        
        return success

# Global instance
pdf_service = PDFService()