from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import InterviewStart, QuestionGenerateOut, AnswerInput # Import AnswerInput
from app.services.interview_service import InterviewService
from typing import Union, Dict, Any

router = APIRouter()

@router.post("/start", response_model=QuestionGenerateOut, tags=["Interview"])
def start_interview_session(
    session_data: InterviewStart, 
    db: Session = Depends(get_db)
):
    """
    Memulai sesi wawancara baru. 
    Langkah C: Membuat entri sesi, memanggil RAG, dan menghasilkan pertanyaan LLM pertama.
    """
    
    # 1. Inisialisasi Service (Dependency Injection)
    interview_service = InterviewService(db)

    # 2. Logika Pemanggilan dan Penanganan Error
    try:
        # Panggil fungsi inti yang melakukan RAG dan LLM di service layer
        return interview_service.start_new_interview(session_data)
    except ValueError as e:
        # Contoh: Jika Mahasiswa ID atau Role ID tidak ditemukan
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        # Menangani error umum (misalnya LLM API error, kesalahan DB, dll.)
        print(f"FATAL ERROR IN INTERVIEW START: {e}") # Log error di server
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gagal memulai sesi karena kesalahan internal.")

# ---------------------------------------------------
# ENDPOINT BARU: SUBMIT JAWABAN DAN LANJUTKAN
# ---------------------------------------------------
@router.post("/answer", tags=["Interview"])
def submit_answer(
    answer_data: AnswerInput, 
    is_final: bool = False, # Query parameter untuk memaksa sesi berakhir
    db: Session = Depends(get_db)
) -> Union[QuestionGenerateOut, Dict[str, str]]:
    """
    Menerima jawaban mahasiswa, mengevaluasi, menyimpan skor, dan menghasilkan pertanyaan lanjutan
    atau mengakhiri sesi.
    """
    
    interview_service = InterviewService(db)
    
    try:
        # Panggil fungsi inti di service
        result = interview_service.submit_answer_and_continue(answer_data, is_final_question=is_final)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        print(f"ERROR processing answer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gagal memproses jawaban atau LLM gagal merespons.")
