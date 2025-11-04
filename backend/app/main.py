from fastapi import FastAPI
from app.core.config import settings
from app.api import user_router 
from app.api import pipeline_router 
from app.api import interview_router # <-- ROUTER BARU DARI LANGKAH C

# 1. Inisialisasi Aplikasi FastAPI
# Logic: Titik masuk utama aplikasi. Semua konfigurasi dimuat dari settings.
app = FastAPI(
    title="AI Mock Interview System API",
    version="1.0.0",
    description="Backend API untuk sistem latihan wawancara berbasis LLM"
)

# 2. Endpoints Dasar (Testing)
@app.get("/")
def read_root():
    # Logic: Endpoint sederhana untuk memverifikasi server berjalan
    return {"message": "AI Mock Interview System API is running."}

@app.get("/config")
def show_config():
    # Logic: Menampilkan konfigurasi yang dimuat dari .env (Hanya untuk debugging)
    return {"db_name": settings.DB_NAME, "db_host": settings.DB_HOST}


# 3. Menambahkan Semua Router (Penerapan SRP/DIP)
# Logic: Delegasikan penanganan endpoint ke masing-masing router yang bertanggung jawab.
app.include_router(user_router, prefix="/api/v1/user", tags=["Users"]) 
app.include_router(pipeline_router, prefix="/api/v1/pipeline", tags=["Pipeline"])
app.include_router(interview_router, prefix="/api/v1/interview", tags=["Interview"])
