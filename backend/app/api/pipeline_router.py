# File: backend/app/api/pipeline_router.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.services.job_role_service import JobRoleService
from app.services.cv_service import CvService
from app.schemas import JobRoleOut, CvDataOut

router = APIRouter()

# ---------------------------------------------------
# ENDPOINT 1: GET SEMUA JOB ROLES
# ---------------------------------------------------
@router.get("/job-roles", response_model=List[JobRoleOut], tags=["Pipeline"])
def get_job_roles(db: Session = Depends(get_db)):
    """Mengambil daftar semua peran pekerjaan yang tersedia."""
    # Logic: Memanggil service yang bertanggung jawab atas data Role.
    role_service = JobRoleService(db)
    roles = role_service.get_all_job_roles()
    
    if not roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Roles belum tersedia.")
    return roles

# ---------------------------------------------------
# ENDPOINT 2: UPLOAD CV
# ---------------------------------------------------
@router.post("/upload-cv/{mahasiswa_id}", response_model=CvDataOut, tags=["Pipeline"])
async def upload_cv(
    mahasiswa_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """Menerima file CV (PDF) dan memulai proses parsing."""
    # Logic: Memastikan file yang diupload adalah PDF sebelum diproses.
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File harus berformat PDF.")

    if file.size > 5 * 1024 * 1024: # Batasan 5MB
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Ukuran file maksimal 5MB.")

    # Membaca isi file secara asinkron
    file_content = await file.read()
    
    # Logic: Memanggil service yang bertanggung jawab menyimpan dan memproses CV.
    cv_service = CvService(db)
    
    try:
        db_cv = cv_service.save_cv_data(
            mahasiswa_id=mahasiswa_id,
            file_name=file.filename,
            file_content=file_content
        )
        return db_cv
    except Exception as e:
        print(f"Error saving CV: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gagal memproses CV.")

# ---------------------------------------------------
# ENDPOINT 3: GET RIWAYAT CV (untuk halaman Profil)
# ---------------------------------------------------
@router.get("/cv-history/{mahasiswa_id}", response_model=List[CvDataOut], tags=["Pipeline"])
def get_cv_history(mahasiswa_id: int, db: Session = Depends(get_db)):
    """Mengambil riwayat CV yang pernah diunggah oleh mahasiswa."""
    cv_service = CvService(db)
    history = cv_service.get_cv_history(mahasiswa_id)
    return history