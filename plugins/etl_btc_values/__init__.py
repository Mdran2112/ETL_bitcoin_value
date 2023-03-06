from datetime import date, datetime
import sys

sys.path.append("/opt/airflow")

TICKERS = [
    "NVDA",  # NVidia
    "TSLA",  # Tesla
    "MSFT",  # Microsoft
    "AMZN",  # Amazon
    "AMD",  # AMD
    "INTC"  # Intel
]

def today(): return date.today().strftime("%Y-%m-%d") # datetime.now().strftime("%Y-%m-%d %H:%M:%S")
