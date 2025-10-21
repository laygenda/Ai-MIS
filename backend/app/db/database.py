# File: backend/app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# 1. Membuat Engine Koneksi
# Logic: Menggunakan URL yang dihasilkan di core/config.py
engine = create_engine(
    settings.DATABASE_URL,
    echo=False  # Ganti True untuk melihat SQL yang dieksekusi (debugging)
)

# 2. Membuat Session Lokal
# Logic: Session ini akan digunakan oleh service untuk berinteraksi dengan DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Basis Deklaratif
# Logic: Ini adalah basis kelas yang akan diwarisi oleh semua model ORM Anda
Base = declarative_base()

# Fungsi Dependency untuk mendapatkan Session DB
# Logic: Digunakan di router/endpoint FastAPI (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()