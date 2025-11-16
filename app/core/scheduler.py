# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

"""import importlib

try:
	AsyncIOScheduler = importlib.import_module("apscheduler.schedulers.asyncio").AsyncIOScheduler
except (ImportError, AttributeError) as e:
	raise ImportError("apscheduler is required for AsyncIOScheduler; install it with: pip install APScheduler") from e"""

# 全域單例
scheduler = AsyncIOScheduler()
