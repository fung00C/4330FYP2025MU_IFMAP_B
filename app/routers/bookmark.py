# app/routers/bookmarks.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models import Bookmark, User, BookmarkCreate,BookmarkResponse
from app.database import SessionLocal

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/bookmark", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark: BookmarkCreate,
    current_user: User = Depends(get_current_user),  # Using the current user's email
    db: Session = Depends(get_db)
):
    db_bookmark = Bookmark(
        user_email=current_user.email,
        stock_symbol=bookmark.stock_symbol
    )
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.delete("/{symbol}", response_model=BookmarkResponse)
async def delete_bookmark(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_bookmark = db.query(Bookmark).filter(
        Bookmark.user_email == current_user.email,
        Bookmark.stock_symbol == symbol
    ).first()

    if db_bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(db_bookmark)
    db.commit()
    return db_bookmark

"""@router.get("/", response_model=List[BookmarkResponse])
async def get_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookmarks = db.query(Bookmark).filter(Bookmark.user_email == current_user.email).all()
    return bookmarks
"""