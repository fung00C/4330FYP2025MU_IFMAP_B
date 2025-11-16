# app/main.py
from fastapi import FastAPI
from app.core.lifespan import lifespan

from app.routers.health import router as health_router
from app.routers.tables import router as tables_router
from app.routers.tickers import router as tickers_router
from app.routers.prices import router as prices_router
from app.routers.update import router as update_router

app = FastAPI(lifespan=lifespan, title="Server", description="Service the finance app")

# API endpoints
app.include_router(health_router)
app.include_router(tables_router)
app.include_router(tickers_router)
app.include_router(prices_router)
app.include_router(update_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
