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
    __tablename__ = "bookmark"  # Table for bookmarks

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column('email', String, ForeignKey("user.email"), nullable=False)
    stock_symbol = Column(String, nullable=False)
    
    # Relationship to User model
    user = relationship("User", back_populates="bookmarks")

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
    stock_symbol: str

class BookmarkResponse(BaseModel):
    user_email: str
    stock_symbol: str

    class Config:
        orm_mode = True