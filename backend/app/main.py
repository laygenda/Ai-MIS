# File: backend/app/main.py

from fastapi import FastAPI
from app.core.config import settings

# File: backend/app/main.py

from fastapi import FastAPI
from app.core.config import settings
from app.api import user_router 
from app.api import pipeline_router # <-- IMPORT ROUTER BARU

app = FastAPI(
    title="AI Mock Interview System API",
    version="1.0.0",
    description="Backend API untuk sistem latihan wawancara berbasis LLM"
)

# ... (read_root dan show_config) ...

# 3. Menambahkan Router
app.include_router(user_router.router, prefix="/api/v1/user", tags=["Users"]) 
app.include_router(pipeline_router.router, prefix="/api/v1/pipeline", tags=["Pipeline"]) # <-- TAMBAHKAN INI

# 1. Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="AI Mock Interview System API",
    version="1.0.0",
    description="Backend API untuk sistem latihan wawancara berbasis LLM"
)

# 2. Endpoints Dasar (Testing)
@app.get("/")
def read_root():
    return {"message": "AI Mock Interview System API is running."}

@app.get("/config")
def show_config():
    # Menggunakan objek setting dari core/config
    return {"db_name": settings.DB_NAME, "db_host": settings.DB_HOST}


# 3. Menambahkan Router (Nanti di Langkah Selanjutnya)
# from app.api import user_router
# app.include_router(user_router.router, prefix="/api/v1/user", tags=["Users"])


# Cara menjalankan aplikasi ini di terminal:
# uvicorn app.main:app --reload --app-dir backend