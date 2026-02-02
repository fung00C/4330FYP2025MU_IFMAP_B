# app/models.py
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"  # Match the table name in your SQL
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    bookmarks = relationship("Bookmark", back_populates="user")


class Bookmark(Base):
    __tablename__ = "bookmark"  # Adjusted to plural form for consistency

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("user.email"), nullable=False)
    stock_symbol = Column(String, nullable=False)
    
    # Relationship to User model (optional, but useful for validation/loading user data)
    user = relationship("User", back_populates="bookmark")

User.bookmark = relationship("Bookmark", order_by=Bookmark.id, back_populates="user")

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    email: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class BookmarkCreate(BaseModel):
    email: str
    stock_symbol: str

class BookmarkResponse(BaseModel):
    email: str
    stock_symbol: str

    class Config:
        orm_mode = True