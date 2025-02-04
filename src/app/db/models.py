from sqlalchemy import Column, Integer, String, ForeignKey, JSON, TIMESTAMP, Text
from sqlalchemy.orm import relationship, declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=True)
    file_path = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    doc_metadata = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete")

    def __repr__(self):
        return f"<Document(title={self.title}, file_path={self.file_path})>"

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    chunk_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    document = relationship("Document", back_populates="embeddings")

    def __repr__(self):
        return f"<DocumentEmbedding(document_id={self.document_id}, chunk_index={self.chunk_index})>"
