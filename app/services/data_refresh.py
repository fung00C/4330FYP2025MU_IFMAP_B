# app/services/data_refresh.py
from typing import List

from app.utils.app_state import set_tickers, get_tickers

def refresh_tickers_list(failed_tickers: List[str]) -> None:
    old_tickers = get_tickers()
    new_tickers = [ticket for ticket in old_tickers if ticket not in failed_tickers]
    print(old_tickers)
    print(new_tickers)
    set_tickers(new_tickers)