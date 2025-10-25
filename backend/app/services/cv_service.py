# File: backend/app/services/cv_service.py

from sqlalchemy.orm import Session
from app.db.models import CvData # Model ORM
from app.db.models import Mahasiswa
from datetime import datetime
from typing import Optional
# Pustaka untuk parsing CV (Contoh: PyMuPDF - perlu instalasi 'pip install PyMuPDF')
import fitz # PyMuPDF

class CvService:
    def __init__(self, db: Session):
        self.db = db

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Fungsi pembantu untuk mengekstrak teks dari file PDF."""
        # Logic: Sesuai proposal, ekstraksi teks dari CV/Resume[cite: 70].
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
        """Menyimpan data CV ke PostgreSQL dan memulai proses ekstraksi."""
        
        # 1. Ekstraksi teks mentah
        raw_text = self.extract_text_from_pdf(file_content)
        
        # 2. Proses Parse Kompetensi (Placeholder untuk LLM di tahap selanjutnya)
        # Di sini NANTI akan ada pemanggilan ke LLM/Vector DB untuk menghasilkan parsed_kompetensi
        parsed_kompetensi_placeholder = "Kompetensi dasar berhasil diekstrak."

        # 3. Simpan ke database
        db_cv = CvData(
            mahasiswa_id=mahasiswa_id,
            file_name=file_name,
            raw_text=raw_text,
            parsed_kompetensi=parsed_kompetensi_placeholder,
            tgl_upload=datetime.now()
        )
        self.db.add(db_cv)
        self.db.commit()
        self.db.refresh(db_cv)
        return db_cv

    def get_cv_history(self, mahasiswa_id: int) -> List[CvData]:
        """Mengambil riwayat upload CV mahasiswa tertentu."""
        return self.db.query(CvData).filter(CvData.mahasiswa_id == mahasiswa_id).all()