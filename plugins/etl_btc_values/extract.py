
import json
import logging
from typing import Dict, List

import pandas as pd
import requests
from tabulate import tabulate
from yfinance import Ticker


def run(tickers: List[str], current_day: str) -> Dict[str, pd.DataFrame]:
    raw_dfs = {}

    # Data from NASDAQ
    logging.info(f"Getting info for: {json.dumps(tickers)}")
    day_index = pd.to_datetime([current_day])

    for ticker in tickers:
        tk = Ticker(ticker)
        raw_df = pd.DataFrame(tk.history(period="1d"))
        raw_df.columns = raw_df.columns.str.lower()
        raw_df = raw_df[["open", "high", "low", "close"]]

        raw_dfs[ticker] = raw_df

    # Bitcoin data
    logging.info(f"Getting BTC info...")
    btc_raw = requests.get("https://api.coinbase.com/v2/prices/spot?currency=USD").json()
    btc_raw = float(btc_raw["data"]["amount"])

    btc_raw = pd.DataFrame({'btc_usd': btc_raw}, index=day_index)

    raw_dfs["btc_usd"] = btc_raw

    logging.info(f"Raw data:")
    for k, df in raw_dfs.items():
        logging.info(k)
        logging.info(tabulate(df, headers='keys', tablefmt='psql'))
    return raw_dfs

