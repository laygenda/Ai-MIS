from app.services.llm_service import LLMService
from typing import Dict, Any, Tuple
from decimal import Decimal
import json

class EvaluationService:
    """
    Modul Tingkat Rendah untuk menilai jawaban menggunakan LLM dan Guardrails.
    Tanggung jawab: Menghasilkan skor numerik dan narasi feedback.
    """
    def __init__(self):
        self.llm_service = LLMService()

    def _get_evaluation_system_prompt(self, job_role: str) -> str:
        """
        Menyusun System Instruction untuk LLM Evaluator.
        Logic: Memaksa LLM untuk bertindak sebagai penilai objektif dan menggunakan JSON output.
        """
        return (
            f"Anda adalah sistem evaluator AI yang sangat objektif dan ketat dalam proses wawancara "
            f"untuk peran '{job_role}'. Tugas Anda adalah menilai jawaban kandidat "
            f"berdasarkan rubrik STAR dan Kualitas Komunikasi. "
            f"Setelah penilaian, berikan saran perbaikan konkret. "
            f"OUTPUT HARUS BERUPA JSON MURNI (tanpa teks penjelasan lain) dengan format:\n"
            f"{{\n"
            f'  "skor_situation": 0.00,\n'
            f'  "skor_task": 0.00,\n'
            f'  "skor_action": 0.00,\n'
            f'  "skor_result": 0.00,\n'
            f'  "skor_relevance": 0.00,\n'
            f'  "skor_clarity": 0.00,\n'
            f'  "skor_confidence": 0.00,\n'
            f'  "feedback_narasi": "Saran perbaikan untuk jawaban ini.",\n'
            f'  "saran_utama": "Poin perbaikan paling penting."\n'
            f"}}"
        )

    def evaluate_answer(self, job_role: str, question: str, answer_clean: str) -> Tuple[Dict[str, Decimal], str, str]:
        """
        Melakukan evaluasi LLM dan mengembalikan skor, feedback narasi, dan saran utama.
        """
        
        system_prompt = self._get_evaluation_system_prompt(job_role)
        
        user_prompt = (
            f"Pertanyaan Pewawancara:\n---\n{question}\n---\n"
            f"Jawaban Mahasiswa (Setelah Preprocessing):\n---\n{answer_clean}\n---\n"
            f"Instruksi Penilaian:\n"
            f"1. Nilai setiap aspek (S, T, A, R, Relevance, Clarity) dalam skala 0 hingga 100.\n"
            f"2. Gunakan metode STAR jika pertanyaan berbasis perilaku (Behavioral).\n"
            f"3. Jika jawaban terlalu pendek atau tidak relevan, skor relevansi harus rendah.\n"
            f"4. Berikan Feedback Narasi dan Saran Utama (Key Takeaway)."
        )

        raw_json_output = self.llm_service.generate_content(system_prompt, user_prompt)
        
        # Penanganan error LLM (Jika API Key salah, dll.)
        if not raw_json_output or raw_json_output.startswith("ERROR"):
            raise Exception(f"LLM Gagal menghasilkan evaluasi: {raw_json_output}")

        try:
            # Logic: Membersihkan dan parsing JSON murni dari output LLM
            # Hapus markdown artifacts yang mungkin ditambahkan oleh LLM
            cleaned_json_str = raw_json_output.strip().replace('```json', '').replace('```', '')
            evaluation_data = json.loads(cleaned_json_str)
            
            # Memastikan skor adalah Decimal untuk presisi
            scores = {
                k: Decimal(str(v)) for k, v in evaluation_data.items() if k.startswith('skor_')
            }
            
            # Mengambil feedback naratif
            narasi = evaluation_data.get('feedback_narasi', 'Tidak ada feedback naratif.')
            saran = evaluation_data.get('saran_utama', 'Perlu struktur jawaban yang lebih baik.')
            
            return scores, narasi, saran

        except json.JSONDecodeError as e:
            # Jika LLM tidak memberikan JSON murni (Pelanggaran Prompt)
            print(f"JSON Parsing Error: {e}\nRaw Output: {raw_json_output}")
            raise Exception("LLM memberikan format output yang salah. Perlu perbaikan Prompt Engineering.")
