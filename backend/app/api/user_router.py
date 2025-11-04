from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import MahasiswaCreate, MahasiswaOut # Import skema Mahasiswa
from app.services.user_service import UserService # Import User Service

router = APIRouter()

# ---------------------------------------------------
# ENDPOINT 1: REGISTRASI PENGGUNA BARU
# ---------------------------------------------------
@router.post("/register", response_model=MahasiswaOut, status_code=status.HTTP_201_CREATED)
def register_user(user: MahasiswaCreate, db: Session = Depends(get_db)):
    """
    Mendaftarkan mahasiswa baru ke dalam sistem.
    """
    # 1. Inisialisasi Service (Dependency Injection)
    user_service = UserService(db)
    
    # 2. Cek duplikasi email
    db_user = user_service.get_mahasiswa_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email sudah terdaftar.")

    # 3. Buat user melalui service
    # Logic: Logika hashing password dan penyimpanan diurus oleh UserService
    try:
        new_user = user_service.create_mahasiswa(user)
        return new_user
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gagal mendaftarkan pengguna.")

# ---------------------------------------------------
# ENDPOINT 2: LOGIN (Placeholder untuk Autentikasi)
# ---------------------------------------------------
# Nanti Anda akan menambahkan endpoint login di sini yang mengembalikan token.