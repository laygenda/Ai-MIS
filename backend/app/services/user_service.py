from sqlalchemy.orm import Session
from app.db.models import Mahasiswa
from app.schemas import MahasiswaCreate
from passlib.context import CryptContext
from typing import Optional

# Konteks untuk Hashing Password (Menggunakan bcrypt)
# Logic: Ini adalah guardrail keamanan. Jangan pernah menyimpan password mentah.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """
    Modul Tingkat Rendah untuk Logika Bisnis Mahasiswa (User).
    Tanggung jawab tunggal: Interaksi DB dan Hashing Password.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_mahasiswa_by_email(self, email: str) -> Optional[Mahasiswa]:
        """Mencari mahasiswa berdasarkan email (digunakan untuk cek duplikasi saat register)."""
        return self.db.query(Mahasiswa).filter(Mahasiswa.email == email).first()

    def create_mahasiswa(self, user: MahasiswaCreate) -> Mahasiswa:
        """Mendaftarkan mahasiswa baru setelah menghash password."""
        
        # 1. Hashing Password
        # Logic: Menggunakan CryptContext untuk mengubah password mentah menjadi hash yang aman.
        hashed_password = self._hash_password(user.password)
        
        # 2. Membuat objek Model ORM
        db_user = Mahasiswa(
            nama=user.nama,
            email=user.email,
            # Simpan hash, bukan password mentah
            password_hash=hashed_password, 
            no_hp=user.no_hp
        )
        
        # 3. Menyimpan ke database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def _hash_password(self, password: str) -> str:
        """Fungsi pembantu untuk hashing password."""
        return pwd_context.hash(password)