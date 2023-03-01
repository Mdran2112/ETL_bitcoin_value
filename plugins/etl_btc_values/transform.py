import logging
import os
from typing import Dict

import pandas as pd
import numpy as np
from tabulate import tabulate

from plugins.etl_btc_values import TICKERS


def run(raw_dfs: Dict[str, pd.DataFrame]):

    # Feature engineering
    raw_dfs = raw_dfs.copy()
    tickers = TICKERS.copy()

    logging.info("Aplying feature engineering")
    for ticker in tickers:
        df = raw_dfs[ticker]
        df["dif_open_close"] = df["open"] - df["close"]
        df["range_day"] = df["high"] - df["low"]
        df["sign_day"] = np.where(df["dif_open_close"] > 0.0, "+", np.where(df["dif_open_close"] < 0.0, "-", "0"))

        df = df[["close", "dif_open_close", "range_day", "sign_day"]]
        df.columns = map(lambda x: ticker.lower() + "_" + x, list(df.columns))

        raw_dfs[ticker] = df.tz_localize(None)

    # Concat
    logging.info("Merging data...")
    table = pd.concat(raw_dfs.values(), axis=1)
    table["date"] = table.index
    table = table.reset_index(drop=True)
    table = table[["date"] + list(table.columns)[:-1]]
    logging.info("Data transformed!")
    logging.info(tabulate(table, headers='keys', tablefmt='psql'))
    return table
