# app/utils/json_helper.py
import json
import os
from functools import lru_cache

# load and cache stock category mapping
@lru_cache(maxsize=1)
def load_stock_category_map() -> dict:
    """
    Load and cache a mapping of ticker -> (sector, industry).
    Expects the JSON at `<repo_root>/json/stock_category.json` with structure:
    { "data": [ { "Sector": { "Industry": ["TICK1", ...] } }, ... ] }
    """
    # Determine repo root relative to this file
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    json_path = os.path.join(root_dir, 'json', 'stock_category.json')
    mapping = {}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        for sector_obj in payload.get('data', []):
            # sector_obj is like { "Technology": { "Semiconductors": ["NVDA", ...] } }
            for sector, industries in sector_obj.items():
                for industry, tickers in industries.items():
                    for t in tickers:
                        mapping[str(t).upper()] = (sector, industry)
    except Exception:
        # On error, return empty mapping
        return {}
    return mapping