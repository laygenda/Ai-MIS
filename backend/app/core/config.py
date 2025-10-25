# File: backend/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Memuat .env file
# Logic: Ini memastikan konfigurasi DB tersedia untuk modul lain.
class Settings(BaseSettings):
    # Mengatur lokasi file .env
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'), extra='ignore')

    # Konfigurasi Database
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    # ------------------------------------
    # KONFIGURASI AI / VECTOR DB BARU
    # ------------------------------------
    CHROMA_DB_PATH: str = "./chroma_data" # Direktori penyimpanan data ChromaDB
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2" # Model yang cepat dan efisien
    # Konfigurasi LLM
    GEMINI_API_KEY: str

    @property
    def DATABASE_URL(self) -> str:
        # Menghasilkan URL koneksi PostgreSQL
        # Format: postgresql+psycopg2://USER:PASSWORD@HOST:PORT/NAME
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Instansiasi objek setting
# Logic: Objek ini akan di-inject ke modul lain (Dependency Injection).
settings = Settings()