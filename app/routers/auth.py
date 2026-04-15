# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import UserCreate, User, Token
from app.database import SessionLocal  # Import the session
import bcrypt
import logging
from jose import JWTError, jwt
from datetime import datetime, timedelta
logger = logging.getLogger("auth_logger")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("login.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(file_handler)

SECRET_KEY = "123"  # Update this with your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 500

router = APIRouter()

# Dependency for getting a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning("Email %s already registered", user.email)
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(email=user.email, password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("User created successfully: %s", user.email)
    return {"message": "User created successfully"}
@router.post("/login")
async def login(user: UserCreate, db: Session = Depends(get_db)):
    logger.info("Login attempt for user: %s", user.email)
    # Check if the user exists
    for handler in logging.root.handlers:
        handler.flush()
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid User")
    
    # Check the password
    if not bcrypt.checkpw(user.password.encode('utf-8'), existing_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid Password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": existing_user.email}, expires_delta=access_token_expires
    )
    logger.info("Login Successfully")
    return {"access_token": access_token, "token_type": "bearer"}