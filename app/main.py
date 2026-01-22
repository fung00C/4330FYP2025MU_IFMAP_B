# app/main.py
from fastapi import FastAPI
from app.core.lifespan import lifespan

from app.routers.health import router as health_router
from app.routers.tables import router as tables_router
from app.routers.tickers import router as tickers_router
from app.routers.prices import router as prices_router
from app.routers.update import router as update_router
from app.routers.detail import router as detail_router
from app.routers.category import router as category_router
from app.routers.recomendation import router as recomendation_router
from app.routers.rank import router as rank_router
from app.routers.auth import router as auth_router
from app.utils.app_state import set_user_db, get_user_db
from app.database import init_db
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
app = FastAPI(lifespan=lifespan, title="Server", description="Service the finance app")
init_db()
# API endpoints
app.include_router(health_router)
app.include_router(tables_router)
app.include_router(tickers_router)
app.include_router(prices_router)
app.include_router(update_router)
app.include_router(detail_router)
app.include_router(category_router)
app.include_router(recomendation_router)
app.include_router(rank_router)
app.include_router(auth_router)

# Configure a CORS intermediary to allow requests from the React frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Adjust according to your React port.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)