# app/services/data_refresh.py
from typing import List

from app.utils.app_state import set_tickers, get_tickers

def refresh_tickers_list(failed_tickers: List[str]) -> None:
    origin_tickers = get_tickers()
    renew_tickers = [ticket for ticket in origin_tickers if ticket not in failed_tickers]
    print(f"🔄 Refreshing tickers list. \n| Original: {origin_tickers} \n| Failed: {failed_tickers} \n| Renewed: {renew_tickers}")
    set_tickers(renew_tickers)