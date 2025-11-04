# File: backend/app/services/interview_service.py

from sqlalchemy.orm import Session
from app.db.models import InterviewSession, PerQuestions, JobRole, Mahasiswa, CvData, EvaluationMetrics, Feedback # Import Model Baru
from app.schemas import InterviewStart, QuestionGenerateOut, AnswerInput
from app.services.rag_service import RAGService 
from app.services.llm_service import LLMService 
from app.services.evaluation_service import EvaluationService # <-- IMPORT BARU
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, Union
from decimal import Decimal

class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        self.rag_service = RAGService()
        self.llm_service = LLMService()
        self.evaluation_service = EvaluationService()

    # ----------------------------------------------------------------------
    # FUNGSI PEMBANTU UNTUK MENGAMBIL DATA DASAR
    # ----------------------------------------------------------------------
    def _fetch_session_data(self, session_data: InterviewStart):
        """Mengambil data Mahasiswa, Role, dan CV yang dibutuhkan dari PostgreSQL."""
        mahasiswa = self.db.query(Mahasiswa).filter(Mahasiswa.mahasiswa_id == session_data.mahasiswa_id).first()
        job_role = self.db.query(JobRole).filter(JobRole.role_id == session_data.role_id).first()
        cv_data = self.db.query(CvData).filter(CvData.cv_id == session_data.cv_id).first()
        
        if not all([mahasiswa, job_role, cv_data]):
            raise ValueError("Data Mahasiswa, Role, atau CV tidak ditemukan.")
            
        return mahasiswa, job_role, cv_data

    # ----------------------------------------------------------------------
    # FUNGSI UTAMA: MEMULAI WAWANCARA (START INTERVIEW)
    # ----------------------------------------------------------------------
    def start_new_interview(self, session_data: InterviewStart) -> QuestionGenerateOut:
        """
        Langkah C: Memulai sesi baru, memanggil RAG, dan menghasilkan pertanyaan pertama.
        """
        
        # 1. Fetch Data dari PostgreSQL
        mahasiswa, job_role, cv_data = self._fetch_session_data(session_data)
        
        # 2. Buat Entri Sesi Baru di PostgreSQL
        db_session = InterviewSession(
            mahasiswa_id=mahasiswa.mahasiswa_id,
            role_id=job_role.role_id,
            tgl_mulai=datetime.now(),
            skor_total_rata_rata=0.00 # Skor awal 0
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        # 3. Lakukan Retrieval (RAG)
        # Logic: Cari konteks CV yang paling relevan dengan Job Role
        rag_query = f"Pengalaman atau kompetensi apa yang paling menonjol terkait peran {job_role.nama_role}?"
        relevant_cv_context = self.rag_service.retrieve_relevant_context(
            mahasiswa_id=mahasiswa.mahasiswa_id, 
            query_text=rag_query, 
            n_results=5
        )
        
        # 4. Prompt Engineering (Membuat System Instruction)
        # Logic: Mengatur persona LLM dan memberikan semua konteks yang dikumpulkan.
        system_instruction = (
            f"Anda adalah pewawancara HR profesional untuk peran '{job_role.nama_role}' "
            f"di perusahaan teknologi. Tanyakan pertanyaan pembuka yang PERSONAL "
            f"berdasarkan konteks CV yang disediakan. Tanyakan hanya SATU pertanyaan."
        )
        
        user_prompt = (
            f"Tugas Anda: Ajukan pertanyaan pembuka. \n\n"
            f"Data Mahasiswa: Nama={mahasiswa.nama}, Role Tujuan='{job_role.nama_role}'. \n"
            f"Konteks CV Paling Relevan (RAG): ```{relevant_cv_context}``` \n\n"
            f"Pertanyaan Anda harus mengacu pada informasi di bagian Konteks CV tersebut. "
            f"Contoh: 'Berdasarkan proyek Anda di [Proyek A] yang terkait dengan [Topik di CV], bagaimana Anda menangani...?'"
        )
        
        # 5. Panggil LLM Service
        pertanyaan_llm = self.llm_service.generate_content(system_instruction, user_prompt)

        # 6. Simpan Pertanyaan Pertama ke PostgreSQL
        db_question = PerQuestions(
            session_id=db_session.session_id,
            urutan_pertanyaan=1,
            jenis_pertanyaan="Pembuka (RAG)",
            pertanyaan_llm=pertanyaan_llm if pertanyaan_llm and not pertanyaan_llm.startswith("ERROR") else "Maaf, terjadi kesalahan saat membuat pertanyaan.",
            waktu_tanya=datetime.now()
        )
        self.db.add(db_question)
        self.db.commit()
        self.db.refresh(db_question)
        
        # 7. Mengembalikan Respons Output
        return QuestionGenerateOut(
            qa_id=db_question.qa_id,
            session_id=db_session.session_id,
            urutan_pertanyaan=1,
            jenis_pertanyaan=db_question.jenis_pertanyaan,
            pertanyaan_llm=db_question.pertanyaan_llm
        )

# ----------------------------------------------------------------------
    # FUNGSI BARU: MENERIMA JAWABAN, EVALUASI, DAN LANJUTKAN SESI
    # ----------------------------------------------------------------------
    def submit_answer_and_continue(self, answer_data: AnswerInput, is_final_question: bool = False) -> Union[QuestionGenerateOut, Dict[str, str]]:
        """
        Menerima jawaban, mengevaluasi, menyimpan skor, dan menghasilkan pertanyaan lanjutan.
        """
        # 1. Ambil Data Pertanyaan & Sesi
        db_qa = self.db.query(PerQuestions).filter(PerQuestions.qa_id == answer_data.qa_id).first()
        if not db_qa:
            raise ValueError("Pertanyaan tidak ditemukan.")

        db_session = self.db.query(InterviewSession).filter(InterviewSession.session_id == db_qa.session_id).first()
        job_role = self.db.query(JobRole).filter(JobRole.role_id == db_session.role_id).first()
        
        # 2. Preprocessing Jawaban
        # Logic: Contoh sederhana preprocessing (Anda dapat menambahkan penghitungan filler words di sini)
        answer_clean = answer_data.jawaban_mentah.strip() 
        
        # 3. Lakukan Evaluasi (PANGGIL EVALUATION SERVICE)
        # Logic: EvaluationService akan mengurus LLM Prompting untuk mendapatkan skor dan feedback.
        scores_dict, narasi_feedback, saran_utama = self.evaluation_service.evaluate_answer(
            job_role=job_role.nama_role, 
            question=db_qa.pertanyaan_llm, 
            answer_clean=answer_clean
        )
        
        # 4. Hitung Skor Gabungan dan Kategori
        # Logic: Tentukan skor akhir dan label kategori (A, B, C)
        total_scores = sum(scores_dict.values())
        count = len(scores_dict)
        skor_gabungan = total_scores / count
        label_kategori = "A" if skor_gabungan >= 80 else ("B" if skor_gabungan >= 60 else "C")

        # 5. Update & Simpan Data (PostgreSQL)
        
        # A. Update Jawaban di PER_QUESTIONS
        db_qa.jawaban_mahasiswa_mentah = answer_data.jawaban_mentah
        db_qa.jawaban_mahasiswa_bersih = answer_clean
        db_qa.waktu_respon = answer_data.waktu_respon
        self.db.add(db_qa)

        # B. Simpan EVALUATION_METRICS
        db_metrics = EvaluationMetrics(
            qa_id=db_qa.qa_id,
            skor_gabungan=skor_gabungan,
            label_kategori=label_kategori,
            **scores_dict # Unpack semua skor STAR dan Kualitas
        )
        self.db.add(db_metrics)

        # C. Simpan FEEDBACK
        db_feedback = Feedback(
            qa_id=db_qa.qa_id,
            feedback_narasi_llm=narasi_feedback,
            saran_perbaikan_utama=saran_utama
        )
        self.db.add(db_feedback)
        
        self.db.commit() # Simpan semua perubahan
        
        # 6. Tentukan Langkah Selanjutnya: Lanjut Pertanyaan atau Akhiri Sesi
        if is_final_question or db_qa.urutan_pertanyaan >= 5: # Batasi maksimum 5 pertanyaan untuk demo
            self.end_interview_session(db_session.session_id)
            return {"status": "Sesi Berakhir", "session_id": db_session.session_id}
        else:
            return self._generate_next_question(db_session.session_id, db_qa)

    # ----------------------------------------------------------------------
    # FUNGSI BARU: GENERATE PERTANYAAN LANJUTAN (PROMPT CHAINING)
    # ----------------------------------------------------------------------
    def _generate_next_question(self, session_id: int, previous_qa: PerQuestions) -> QuestionGenerateOut:
        """
        Menghasilkan pertanyaan lanjutan berdasarkan riwayat percakapan sebelumnya.
        """
        
        # Ambil semua data sesi untuk konteks LLM
        db_session = self.db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
        job_role = self.db.query(JobRole).filter(JobRole.role_id == db_session.role_id).first()
        
        # 1. Prompt Chaining: Berikan Konteks
        # Logic: LLM harus tahu apa yang sudah ditanyakan dan bagaimana jawaban sebelumnya.
        system_instruction = (
            f"Anda adalah pewawancara profesional untuk peran '{job_role.nama_role}'. "
            f"Tugas Anda adalah mengajukan pertanyaan lanjutan (follow-up) atau pertanyaan teknis baru. "
            f"Tanyakan hanya SATU pertanyaan."
        )

        user_prompt = (
            f"Riwayat Percakapan Terakhir (Pertanyaan ke-{previous_qa.urutan_pertanyaan}):\n"
            f"Q: {previous_qa.pertanyaan_llm}\n"
            f"A: {previous_qa.jawaban_mahasiswa_bersih}\n\n"
            f"Instruksi: Berdasarkan jawaban di atas, ajukan SATU pertanyaan LANJUTAN yang lebih spesifik "
            f"(misalnya: 'Bisakah Anda jelaskan lebih detail tentang metode X?') atau "
            f"ajukan pertanyaan TEKNIS baru yang relevan dengan peran '{job_role.nama_role}'."
        )

        pertanyaan_llm = self.llm_service.generate_content(system_instruction, user_prompt)
        
        # 2. Simpan Pertanyaan Baru
        new_qa = PerQuestions(
            session_id=session_id,
            urutan_pertanyaan=previous_qa.urutan_pertanyaan + 1,
            jenis_pertanyaan="Lanjutan (Chaining)",
            pertanyaan_llm=pertanyaan_llm,
            waktu_tanya=datetime.now()
        )
        self.db.add(new_qa)
        self.db.commit()
        self.db.refresh(new_qa)
        
        # 3. Kembalikan Output
        return QuestionGenerateOut(
            qa_id=new_qa.qa_id,
            session_id=session_id,
            urutan_pertanyaan=new_qa.urutan_pertanyaan,
            jenis_pertanyaan=new_qa.jenis_pertanyaan,
            pertanyaan_llm=new_qa.pertanyaan_llm
        )

    # ----------------------------------------------------------------------
    # FUNGSI BARU: MENGAKHIRI SESI
    # ----------------------------------------------------------------------
    def end_interview_session(self, session_id: int):
        """Menghitung skor rata-rata sesi dan menandai sesi selesai."""
        db_session = self.db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
        
        # 1. Ambil semua skor gabungan dari sesi ini
        scores = self.db.query(EvaluationMetrics.skor_gabungan).join(PerQuestions).filter(PerQuestions.session_id == session_id).all()
        
        if scores:
            total_score = sum([s[0] for s in scores])
            avg_score = total_score / len(scores)
            
            # 2. Update sesi
            db_session.skor_total_rata_rata = Decimal(f"{avg_score:.2f}") # Simpan 2 desimal
        
        db_session.tgl_selesai = datetime.now()
        self.db.add(db_session)
        self.db.commit()