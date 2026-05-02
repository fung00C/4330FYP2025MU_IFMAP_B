# 4330FYP2025MU IFMAP Backend

## Overview

This repository contains the FastAPI backend for a finance application built as a final year project. It provides stock and index data ingestion, prediction, recommendation, ranking, and user management features, along with email notification support.

## Key Features

- FastAPI-based REST API backend
- Stock and index data ingestion from finance sources
- ML-based prediction models stored in `models/*.h5`
- Recommendation endpoints for stocks and indices
- Ranking and statistics generation for financial assets
- User authentication, bookmarks, and notification settings
- Email notification scheduling
- SQLite persistence for both user and financial data
- CORS configuration for frontend integration

## Project Structure

- `app/main.py` - FastAPI application entry point
- `app/core/lifespan.py` - startup/shutdown lifecycle management and background initialization
- `app/database.py` - SQLAlchemy database initialization for user data
- `app/models.py` - SQLAlchemy ORM models and Pydantic schemas
- `app/routers/` - API route definitions for health, tickers, prices, auth, user, bookmarks, recommendations, ranking, and more
- `app/services/` - business logic and data ingestion services
- `app/tasks/` - scheduled jobs for updating financial data and sending notifications
- `app/db/` - database connection utilities
- `app/utils/` - shared state and helper utilities
- `json/` - stock category metadata and related JSON files
- `models/` - pre-trained `.h5` prediction models for individual stock symbols
- `sp500_companies.csv` - list of S&P 500 company symbols used by the system

## Dependencies

Install requirements with:

```bash
pip install -r requirements.txt
```

The main dependencies include:

- `fastapi`
- `uvicorn[standard]`
- `pandas`
- `numpy`
- `yfinance`
- `requests`
- `plotly`
- `kaleido`
- `APScheduler`
- `pydantic-settings`
- `pyarrow`

## Running the Application

Start the backend with:

```bash
python -m uvicorn app.main:app --reload
```

The API server listens on `http://127.0.0.1:8000` by default.

## Notes

- The application creates or uses SQLite databases: `user.db` and `financial.db`.
- The startup lifecycle loads stock details, financial tables, predictions, rankings, and schedules update jobs.
- CORS is enabled for `http://localhost:3000` and allows frontend access during development.

## Useful Endpoints

- `/health` - health check
- `/recommendation/stock` - stock recommendation and prediction
- `/recommendation/index` - index recommendation and prediction
- `/auth` - authentication routes
- `/user` - user management
- `/bookmark` - bookmark management
- `/email` - email notification

## Development

- Add or update frontend origin in `app/main.py` if your React app runs on a different host or port.
- Place updated financial model files in the `models/` directory as needed.
- Ensure `json/stock_category.json` and `sp500_companies.csv` remain available for stock metadata ingestion.

---

This README is intended to support backend development, testing, and integration with the frontend finance application.
