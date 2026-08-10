# documrnt used to read and write to table in db for ORM query
# Column, Integer, String, Text, DateTime — SQLAlchemy column types
# they map Python types to postgres types:
# String  → VARCHAR
# Text    → TEXT (unlimited length, good for chunk content)
# Integer → INTEGER
# DateTime → TIMESTAMP
# func    → SQL functions like NOW() — runs on the database side

# Mapped= new SQLAlchemy 2.0 way to type hint columns
# mapped_column= actual column definition
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db import Base
from datetime import datetime

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id:  Mapped[str] = mapped_column(String, index=True) #indexing on session id to fetch fast
    filename:  Mapped[str]  = mapped_column(String)
    chunk_index: Mapped[int]  = mapped_column(Integer)
    content:  Mapped[str]  = mapped_column(Text)
    embedding: Mapped[list] = mapped_column(Vector(768), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())




