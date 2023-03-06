import json
import logging
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests
from tabulate import tabulate
from yfinance import Ticker


def get_ticker_raw_df(ticker: str) -> pd.DataFrame:
    logging.info(f"getting {ticker} data..")
    tk = Ticker(ticker)
    raw_df = pd.DataFrame(tk.history(period="1d"))
    raw_df.columns = raw_df.columns.str.lower()
    raw_df = raw_df[["open", "high", "low", "close"]]
    logging.info(tabulate(raw_df, headers='keys', tablefmt='psql'))
    return raw_df


def get_btc_price(day: pd.DatetimeIndex) -> pd.DataFrame:
    logging.info(f"Getting BTC data...")
    btc_raw = requests.get("https://api.coinbase.com/v2/prices/spot?currency=USD").json()
    price = float(btc_raw["data"]["amount"])
    df = pd.DataFrame({'btc_usd': price}, index=day)
    logging.info(tabulate(df, headers='keys', tablefmt='psql'))
    return df


def run(tickers: List[str], current_day: str) -> Dict[str, pd.DataFrame]:
    raw_dfs = {}

    logging.info(f"Getting info for: {json.dumps(tickers)}")
    day_index = pd.to_datetime([current_day])

    pool = ThreadPoolExecutor(len(tickers) + 1)
    # Get data from NASDAQ and BTC asynchronously
    raw_dfs_list = pool.map(get_ticker_raw_df, tickers)
    raw_btc_price = pool.submit(get_btc_price, day_index)

    for tk, df in zip(tickers, raw_dfs_list):
        raw_dfs[tk] = df
        logging.info(tk)
        logging.info(tabulate(raw_dfs[tk], headers='keys', tablefmt='psql'))

    raw_dfs["btc_usd"] = raw_btc_price.result(timeout=None)

    return raw_dfs
