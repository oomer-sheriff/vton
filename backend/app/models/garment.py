import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from app.db.base_class import Base

class Garment(Base):
    __tablename__ = "garments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    raw_image_path = Column(String, nullable=False)
    processed_image_path = Column(String, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    
    # 384 dimensions for all-MiniLM-L6-v2
    embedding = Column(Vector(384))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
