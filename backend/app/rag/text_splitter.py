from typing import List, Tuple  # Tuple'ı ekleyin!
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def split_text(text: str, metadata: dict = None) -> List[str]:
    """Metni parçalara ayır"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_text(text)
    return chunks

def create_chunks_with_metadata(text: str, pdf_id: str, filename: str) -> Tuple[List[str], List[dict]]:
    """Metadata ile birlikte metin parçaları oluştur"""
    chunks = split_text(text)
    
    # Her chunk için metadata oluştur
    metadata_list = []
    for i, chunk in enumerate(chunks):
        metadata = {
            "pdf_id": pdf_id,
            "filename": filename,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "source": f"{filename}_chunk_{i}"
        }
        metadata_list.append(metadata)
    
    return chunks, metadata_list