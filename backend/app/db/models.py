# File: backend/app/db/models.py

# Model ORM adalah implementasi dari tabel Anda yang mempermudah interaksi DB tanpa harus menulis raw SQL berulang kali (prinsip DRY).

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base # Mengimpor Base dari database.py

# ===============================================
# 1. TABEL MAHASISWA (Users)
# ===============================================
class Mahasiswa(Base):
    __tablename__ = "mahasiswa"

    # Kolom Dasar (Primary Key)
    mahasiswa_id = Column(Integer, primary_key=True, index=True)
    
    # Data Profil
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    no_hp = Column(String(20))
    tgl_registrasi = Column(DateTime(timezone=True))

    # Hubungan (Relationships)
    # Mahasiswa memiliki banyak CV, dan banyak sesi wawancara
    cv_data = relationship("CvData", back_populates="mahasiswa", cascade="all, delete-orphan")
    sessions = relationship("InterviewSession", back_populates="mahasiswa", cascade="all, delete-orphan")


# ===============================================
# 2. TABEL JOB_ROLES (Role Pekerjaan)
# ===============================================
class JobRole(Base):
    __tablename__ = "job_roles"

    role_id = Column(Integer, primary_key=True, index=True)
    nama_role = Column(String(100), unique=True, nullable=False)
    deskripsi = Column(Text)

    # Hubungan
    sessions = relationship("InterviewSession", back_populates="job_role")


# ===============================================
# 3. TABEL CV_DATA (Input Modul 1)
# ===============================================
class CvData(Base):
    __tablename__ = "cv_data"

    cv_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key ke Mahasiswa
    mahasiswa_id = Column(Integer, ForeignKey("mahasiswa.mahasiswa_id", ondelete="CASCADE"), nullable=False)
    
    file_name = Column(String(255))
    raw_text = Column(Text, nullable=False)
    parsed_kompetensi = Column(Text) # Data yang sudah diolah/diekstraksi
    tgl_upload = Column(DateTime(timezone=True))

    # Hubungan
    mahasiswa = relationship("Mahasiswa", back_populates="cv_data")


# ===============================================
# 4. TABEL INTERVIEW_SESSIONS (Riwayat/History)
# ===============================================
class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    mahasiswa_id = Column(Integer, ForeignKey("mahasiswa.mahasiswa_id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("job_roles.role_id", ondelete="RESTRICT"), nullable=False)
    
    # Data Sesi
    tgl_mulai = Column(DateTime(timezone=True))
    tgl_selesai = Column(DateTime(timezone=True))
    skor_total_rata_rata = Column(Numeric(5, 2)) # Skor akhir sesi

    # Hubungan
    mahasiswa = relationship("Mahasiswa", back_populates="sessions")
    job_role = relationship("JobRole", back_populates="sessions")
    questions = relationship("PerQuestions", back_populates="session", cascade="all, delete-orphan")


# ===============================================
# 5. TABEL PER_QUESTIONS (Simulasi Inti Modul 2)
# ===============================================
class PerQuestions(Base):
    __tablename__ = "per_questions"

    qa_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    session_id = Column(Integer, ForeignKey("interview_sessions.session_id", ondelete="CASCADE"), nullable=False)
    
    # Data Tanya Jawab
    urutan_pertanyaan = Column(Integer, nullable=False)
    jenis_pertanyaan = Column(String(50)) # e.g., 'STAR', 'Technical', 'Follow-up'
    pertanyaan_llm = Column(Text, nullable=False)
    jawaban_mahasiswa_mentah = Column(Text) # Output STT/raw input
    jawaban_mahasiswa_bersih = Column(Text) # Setelah NLP Preprocessing
    waktu_respon = Column(Integer) # Waktu dalam detik
    waktu_tanya = Column(DateTime(timezone=True))

    # Hubungan
    session = relationship("InterviewSession", back_populates="questions")
    metrics = relationship("EvaluationMetrics", back_populates="question", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="question", uselist=False, cascade="all, delete-orphan")


# ===============================================
# 6. TABEL EVALUATION_METRICS (Rubrik Skor Modul 3)
# ===============================================
class EvaluationMetrics(Base):
    __tablename__ = "evaluation_metrics"

    metrics_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key (Hubungan 1-to-1 dengan pertanyaan)
    qa_id = Column(Integer, ForeignKey("per_questions.qa_id", ondelete="CASCADE"), unique=True, nullable=False)

    # Skor Rubrik (NUMERIC(5, 2) untuk skor 0.00 hingga 100.00)
    skor_situation = Column(Numeric(5, 2))
    skor_task = Column(Numeric(5, 2))
    skor_action = Column(Numeric(5, 2))
    skor_result = Column(Numeric(5, 2))
    skor_relevance = Column(Numeric(5, 2))
    skor_clarity = Column(Numeric(5, 2))
    skor_confidence = Column(Numeric(5, 2))
    skor_conciseness = Column(Numeric(5, 2))
    
    skor_gabungan = Column(Numeric(5, 2))
    label_kategori = Column(String(10)) # e.g., 'A', 'B', 'C'

    # Hubungan
    question = relationship("PerQuestions", back_populates="metrics")


# ===============================================
# 7. TABEL FEEDBACK (Umpan Balik Narasi Modul 3)
# ===============================================
class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key (Hubungan 1-to-1 dengan pertanyaan)
    qa_id = Column(Integer, ForeignKey("per_questions.qa_id", ondelete="CASCADE"), unique=True, nullable=False)
    
    feedback_narasi_llm = Column(Text, nullable=False) # Saran naratif lengkap
    saran_perbaikan_utama = Column(Text) # Poin perbaikan yang disorot

    # Hubungan
    question = relationship("PerQuestions", back_populates="feedback")