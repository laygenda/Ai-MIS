# File: backend/app/api/interview_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import InterviewStart, QuestionGenerateOut
from app.services.interview_service import InterviewService

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
    # Logic: Inisialisasi service dan menangani error jika ada.
    try:
        interview_service = InterviewService(db)
        # Panggil fungsi inti yang melakukan RAG dan LLM
        return interview_service.start_new_interview(session_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        # Menangani error umum (misalnya API Key salah atau DB bermasalah)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gagal memulai sesi: {e}")
```

### 5. Finalisasi `main.py`

Pastikan Anda telah mengimpor dan menyertakan `interview_router` di `backend/app/main.py`.

```python
# File: backend/app/main.py (Pastikan ini ada)
# ...
from app.api import interview_router # <-- Pastikan ada

app = FastAPI(...)

# ... (Endpoints sebelumnya) ...

# 3. Menambahkan Router
app.include_router(user_router.router, prefix="/api/v1/user", tags=["Users"]) 
app.include_router(pipeline_router.router, prefix="/api/v1/pipeline", tags=["Pipeline"])
app.include_router(interview_router.router, prefix="/api/v1/interview", tags=["Interview"]) # <-- TAMBAHKAN INI
