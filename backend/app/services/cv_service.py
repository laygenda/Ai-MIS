# File: backend/app/services/cv_service.py

from sqlalchemy.orm import Session
from app.db.models import CvData, Mahasiswa 
from datetime import datetime
from typing import Optional
import fitz # PyMuPDF
from app.services.rag_service import RAGService # <-- IMPORT BARU
from typing import Optional, List

class CvService:
    def __init__(self, db: Session):
        self.db = db
        # 1. Inisialisasi RAGService di sini
        # Logic: CvService bertanggung jawab atas ORCHESTRATION antara DB dan Vektor.
        self.rag_service = RAGService() 

    # --- Fungsi extract_text_from_pdf (TETAP SAMA SEPERTI SEBELUMNYA) ---
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Fungsi pembantu untuk mengekstrak teks dari file PDF."""
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return "Extraction Failed"
            
    def save_cv_data(self, mahasiswa_id: int, file_name: str, file_content: bytes):
        """Menyimpan data CV ke PostgreSQL dan memulai proses vectorization (Langkah B)."""
        
        # 1. Ekstraksi teks mentah
        raw_text = self.extract_text_from_pdf(file_content)
        
        # 2. Simpan ke PostgreSQL (CRUD)
        # Logic: Simpan data terstruktur di SQL DB dulu, ini akan memberikan cv_id yang dibutuhkan.
        db_cv = CvData(
            mahasiswa_id=mahasiswa_id,
            file_name=file_name,
            raw_text=raw_text,
            parsed_kompetensi="Belum diproses LLM/Vectorized", # Placeholder awal
            tgl_upload=datetime.now()
        )
        self.db.add(db_cv)
        self.db.commit()
        self.db.refresh(db_cv)
        
        # 3. Panggil RAGService untuk Vectorization (Langkah B)
        # Logic: Ini adalah titik di mana data CV diubah menjadi makna (vektor) dan disimpan di ChromaDB.
        self.rag_service.add_cv_to_vector_db(
            mahasiswa_id=db_cv.mahasiswa_id, 
            cv_id=db_cv.cv_id, 
            raw_text=raw_text
        )

        return db_cv

    # --- Fungsi get_cv_history (TETAP SAMA) ---
    def get_cv_history(self, mahasiswa_id: int) -> List[CvData]:
        """Mengambil riwayat upload CV mahasiswa tertentu."""
        return self.db.query(CvData).filter(CvData.mahasiswa_id == mahasiswa_id).all()
