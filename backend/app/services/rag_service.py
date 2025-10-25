from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from typing import List
import uuid
from app.core.config import settings
import re # Untuk membersihkan teks
import fitz # PyMuPDF (untuk demo chunking)

class RAGService:
    def __init__(self):
        # 1. Inisialisasi ChromaDB Client
        # Logic: Klien ini menghubungkan ke folder penyimpanan data vektor di disk.
        self.client = PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection_name = "cv_kompetensi_collection"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        
        # 2. Inisialisasi Model Embedding
        # Logic: Model ini mengubah teks menjadi array angka (vektor).
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Memecah teks panjang menjadi potongan-potongan kecil (chunks) yang tumpang tindih."""
        # Logic: LLM dan model embedding lebih baik memproses potongan kecil dengan konteks yang utuh.
        
        # Sederhanakan teks untuk memecah berdasarkan spasi atau baris baru
        text = re.sub(r'\s+', ' ', text).strip()
        tokens = text.split(' ')
        chunks = []
        i = 0
        while i < len(tokens):
            chunk = ' '.join(tokens[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks
        
    def add_cv_to_vector_db(self, mahasiswa_id: int, cv_id: int, raw_text: str):
        """Mengubah teks CV menjadi vektor dan menyimpannya di ChromaDB."""
        
        # 1. Chunking Teks
        chunks = self.chunk_text(raw_text)
        
        # 2. Membuat Vektor (Embedding)
        # Logic: Menggunakan model untuk mengodekan setiap chunk menjadi vektor.
        embeddings = self.model.encode(chunks).tolist()
        
        # 3. Menyiapkan Metadata dan IDs
        # Logic: Metadata penting untuk filter pencarian (Hanya cari CV milik mahasiswa tertentu).
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [
            {"mahasiswa_id": mahasiswa_id, "cv_id": cv_id, "source": "cv_upload"} 
            for _ in chunks
        ]
        
        # 4. Menyimpan ke ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"RAGService: Berhasil menambahkan {len(chunks)} chunks CV untuk Mahasiswa ID {mahasiswa_id}")
        
    def retrieve_relevant_context(self, mahasiswa_id: int, query_text: str, n_results: int = 3) -> str:
        """Mencari potongan CV paling relevan berdasarkan kueri (pertanyaan/JD)."""
        
        # 1. Membuat Vektor dari Kueri (Pertanyaan LLM)
        query_embedding = self.model.encode([query_text]).tolist()
        
        # 2. Pencarian (Retrieval)
        # Logic: Mencari n_results chunks yang paling mirip dengan query, 
        # TAPI HANYA dari CV milik mahasiswa_id yang sedang diwawancara.
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"mahasiswa_id": mahasiswa_id} 
        )
        
        # 3. Menggabungkan hasilnya
        if results and results['documents'] and results['documents'][0]:
            context = "\n---\n".join(results['documents'][0])
            return context
        return "Tidak ditemukan konteks CV yang relevan."
