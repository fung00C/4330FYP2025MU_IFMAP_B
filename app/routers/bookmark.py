# app/routers/bookmarks.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models import Bookmark, User, BookmarkCreate
from app.database import SessionLocal

from app.utils.file import open_sql_file
from app.utils.app_state import get_sql_path, get_user_db
import pandas as pd

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add")
async def api_add_bookmark(
    symbol: str,
    email: str,
): 
    sql = open_sql_file(get_sql_path('insert_bookmark'))
    params = (email, symbol)
    con = get_user_db()
    try:
        con.execute(sql, params)
        con.commit()
        return {"message": f"Bookmark for {symbol} added for user {email}"}
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/remove")
async def api_remove_bookmark(
    symbol: str,
    email: str,
):
    sql = open_sql_file(get_sql_path('delete_bookmark'))
    params = (email, symbol)
    con = get_user_db()
    try:
        con.execute(sql, params)
        con.commit()
        return {"message": f"Bookmark for {symbol} removed for user {email}"}
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get")
async def api_get_bookmarks(
    email: str,
):
    sql = open_sql_file(get_sql_path("select_bookmark"))
    con = get_user_db()
    try:
        df = con.execute(sql, (email,)).fetchall()
        con.commit()
        data = [row[0] for row in df]  
        return {"count": len(data), "data": data}
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_with_notify")
async def api_get_bookmarks_with_notify(
    email: str,
):
    sql = open_sql_file(get_sql_path("select_bookmark_notify"))
    con = get_user_db()
    try:
        df = con.execute(sql, (email,)).fetchall()
        con.commit()
        data = [row[0] for row in df]  # Assuming the stock_symbol is the first column and notify is the second column
        return {"count": len(data), "data": data}
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_notify")
async def api_update_bookmark_notify(
    email: str,
    symbol: str
):
    sql = open_sql_file(get_sql_path("update_bookmark_notify"))
    params = (email, symbol)
    con = get_user_db()
    try:
        con.execute(sql, params)
        con.commit()
        return {"message": f"Bookmark for {symbol} updated for user {email}"}
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_notification_setting")
async def api_update_notification_setting(
    email: str,
    frequency: str,
    day_of_week: str = None,
    date_of_month: int = None,
    time_of_day: str = None
):
    sql = open_sql_file(get_sql_path("update_notification_setting"))
    params = (email, frequency, day_of_week, date_of_month, time_of_day)
    con = get_user_db()
    try:
        con.execute(sql, params)
        con.commit()
        return {"message": f"Notification setting updated for user {email}"}
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 



"""
router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Bookmark)
async def create_bookmark(
    bookmark: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Assuming Bookmark model has a field for user_email (if not, add it)
    db_bookmark = Bookmark(
        user_email=current_user.email,  # Assuming the email is in the User model
        stock_symbol=bookmark.stock_symbol
    )
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.delete("/{symbol}", response_model=Bookmark)
async def delete_bookmark(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.stock_symbol == symbol
    ).first()
    
    if db_bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(db_bookmark)
    db.commit()
    return db_bookmark

@router.get("/", response_model=List[Bookmark])
async def get_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    return bookmarks"""