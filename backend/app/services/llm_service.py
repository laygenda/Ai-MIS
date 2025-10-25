from google import genai
from google.genai.errors import APIError
from app.core.config import settings
from typing import Optional

class LLMService:
    """
    Modul Tingkat Rendah untuk interaksi langsung dengan Google Gemini.
    Tanggung jawab tunggal: mengirim prompt dan menerima respons.
    """
    def __init__(self):
        # Inisialisasi Klien Gemini
        # Logic: Memuat kunci API dari settings Pydantic
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash" # Model cepat untuk real-time chat

    def generate_content(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """
        Mengirim System Prompt dan User Prompt ke LLM.
        """
        if not settings.GEMINI_API_KEY:
             return "ERROR: Kunci API Gemini tidak ditemukan. Tidak dapat menghasilkan konten."

        try:
            # Menggunakan System Instruction untuk mengatur persona (Pewawancara)
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7 # Memberi sedikit variasi pada jawaban
                )
            )
            return response.text
        except APIError as e:
            print(f"LLM API Error: {e}")
            return f"Error: Gagal menghubungi LLM. {e}"
        except Exception as e:
            print(f"Unexpected LLM Error: {e}")
            return "Error: Terjadi kesalahan tak terduga pada LLM Service."
