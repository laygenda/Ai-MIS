from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from decimal import Decimal # Digunakan untuk tipe data Numeric dari skor

# ===============================================
# 1. SKEMA MAHASISWA & OTENTIKASI (Modul 1)
# ===============================================

class MahasiswaCreate(BaseModel):
    # Digunakan saat registrasi (Input)
    nama: str
    email: EmailStr # Memastikan format email valid
    password: str # Password mentah dari user
    no_hp: Optional[str] = None

class MahasiswaOut(BaseModel):
    # Digunakan saat menampilkan data Mahasiswa (Output)
    mahasiswa_id: int
    nama: str
    email: EmailStr
    no_hp: Optional[str] = None
    tgl_registrasi: datetime
    
    # Konfigurasi Pydantic untuk membaca atribut dari Model ORM (SQLAlchemy)
    class Config:
        from_attributes = True
        
# -------------------------------------------------
# SKEMA UNTUK AUTENTIKASI (Input Login)
# -------------------------------------------------
class Token(BaseModel):
    # Digunakan untuk respons token setelah login berhasil
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    # Digunakan untuk validasi token (hanya ID user)
    mahasiswa_id: Optional[int] = None

# ===============================================
# 2. SKEMA DATA STATIS (Job Roles & CV Data) (Modul 1)
# ===============================================

class JobRoleOut(BaseModel):
    # Digunakan untuk menampilkan daftar Job Role di Frontend (Output)
    role_id: int
    nama_role: str
    deskripsi: Optional[str] = None
    
    class Config:
        from_attributes = True

class CvDataOut(BaseModel):
    # Digunakan untuk menampilkan riwayat CV yang pernah diupload di Profile (Output)
    cv_id: int
    mahasiswa_id: int
    file_name: str
    parsed_kompetensi: Optional[str] = None
    tgl_upload: datetime
    
    class Config:
        from_attributes = True

# ===============================================
# 3. SKEMA SIMULASI WAWANCARA (Modul 2)
# ===============================================

class InterviewStart(BaseModel):
    # Digunakan saat Mahasiswa menekan tombol "Mulai Interview Baru" (Input)
    mahasiswa_id: int
    role_id: int
    cv_id: int # CV yang akan digunakan untuk personalisasi sesi ini

class QuestionGenerateOut(BaseModel):
    # Respons dari backend saat LLM menghasilkan pertanyaan baru (Output)
    qa_id: int # ID unik untuk interaksi Tanya-Jawab ini
    session_id: int
    urutan_pertanyaan: int
    jenis_pertanyaan: str
    pertanyaan_llm: str # Pertanyaan yang akan diubah menjadi suara (TTS)

    class Config:
        from_attributes = True

class AnswerInput(BaseModel):
    # Jawaban Mahasiswa yang dikirim ke backend (Input)
    qa_id: int # Mengacu pada pertanyaan yang dijawab
    jawaban_mentah: str # Teks dari STT atau input langsung
    waktu_respon: Optional[int] = None # Waktu dalam detik

# ===============================================
# 4. SKEMA EVALUASI DAN FEEDBACK (Modul 3)
# ===============================================

# --- Sub-Skema untuk Metrics ---
class EvaluationMetricsOut(BaseModel):
    # Digunakan untuk menampilkan skor rinci per pertanyaan (Output)
    
    # Skor STAR (menggunakan Decimal untuk presisi)
    skor_situation: Optional[Decimal] = None
    skor_task: Optional[Decimal] = None
    skor_action: Optional[Decimal] = None
    skor_result: Optional[Decimal] = None
    
    # Skor Kualitas Jawaban
    skor_relevance: Optional[Decimal] = None
    skor_clarity: Optional[Decimal] = None
    skor_confidence: Optional[Decimal] = None
    skor_conciseness: Optional[Decimal] = None
    
    skor_gabungan: Optional[Decimal] = None
    label_kategori: Optional[str] = None # 'A', 'B', 'C'
    
    class Config:
        from_attributes = True

# --- Sub-Skema untuk Feedback ---
class FeedbackOut(BaseModel):
    # Digunakan untuk menampilkan saran perbaikan naratif (Output)
    feedback_narasi_llm: str
    saran_perbaikan_utama: Optional[str] = None
    
    class Config:
        from_attributes = True

# -------------------------------------------------
# SKEMA GABUNGAN (Output dari Sesi Wawancara)
# -------------------------------------------------
class QuestionAnswerDetail(BaseModel):
    # Digunakan untuk menampilkan riwayat detail 1 kali Tanya-Jawab
    qa_id: int
    urutan_pertanyaan: int
    pertanyaan_llm: str
    jawaban_mahasiswa_bersih: Optional[str] = None
    
    # Hubungan 1-to-1 dengan Metrics dan Feedback
    metrics: Optional[EvaluationMetricsOut] = None
    feedback: Optional[FeedbackOut] = None

    class Config:
        from_attributes = True
        
# -------------------------------------------------
# SKEMA DASHBOARD & RIWAYAT SESI
# -------------------------------------------------
class InterviewSessionOut(BaseModel):
    # Digunakan untuk menampilkan riwayat sesi di Dashboard (Output)
    session_id: int
    tgl_mulai: datetime
    tgl_selesai: Optional[datetime] = None
    skor_total_rata_rata: Optional[Decimal] = None
    
    # Informasi Role (dapat diakses melalui relationship di ORM)
    job_role: JobRoleOut 
    
    # Daftar semua Q&A dalam sesi (digunakan untuk Report Detail)
    questions: List[QuestionAnswerDetail] = []
    
    class Config:
        from_attributes = True
