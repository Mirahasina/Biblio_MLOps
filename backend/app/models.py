from sqlalchemy import Boolean, Column, Float, Integer, String

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20), default="")
    genre = Column(String(100), default="general")
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)
