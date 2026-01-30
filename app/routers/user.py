from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import User
from app.database import SessionLocal
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from pydantic import BaseModel
import bcrypt



# Constants for JWT settings
SECRET_KEY = "123"  
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
router = APIRouter()

# Dependency for getting a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/user")
async def get_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Validate token and get user information
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Fetch user from the database
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return {"email": user.email}
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.post("/changepassword")
async def change_password(request: ChangePasswordRequest, token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = db.query(User).filter(User.email == email).first()

        # If user not found
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if the old password is correct
        if not bcrypt.checkpw(request.old_password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Old password is incorrect")
        
        # Hash the new password
        hashed_new_password = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed_new_password
        
        db.commit()
        return {"message": "Password changed successfully"}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.delete("/delete")
async def delete_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = db.query(User).filter(User.email == email).first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(user)  
        db.commit()  

        return {"message": "Account deleted successfully"}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")