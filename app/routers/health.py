# app/routers/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Server is running"}
