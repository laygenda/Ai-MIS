# File: backend/app/services/job_role_service.py

from sqlalchemy.orm import Session
from app.db.models import JobRole

class JobRoleService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_job_roles(self):
        """Mengambil semua daftar Job Role yang tersedia dari DB."""
        return self.db.query(JobRole).all()
        
    def get_role_by_id(self, role_id: int):
        """Mengambil detail Job Role berdasarkan ID."""
        return self.db.query(JobRole).filter(JobRole.role_id == role_id).first()