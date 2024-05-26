import os
from enum import Enum

import pandas as pd
import requests
from dotenv import load_dotenv

from src.backend.utils import create_directory


class TimeSpan(str, Enum):
    MINUTE = "minute"


def download_data(data: pd.DataFrame, save_path: str) -> pd.DataFrame:
    create_directory(save_path)
    data.to_csv(save_path)
    return data


def read_data(ticker: str, start: str, end: str, multiplier: int, timespan: TimeSpan) -> pd.DataFrame:
    load_dotenv()
    POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")

    response = requests.get(
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan.value}/{start}/{end}?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
    ).json()
    return pd.DataFrame(response["results"])


# start = "2021-05-01"
# end = "2022-05-01"
# multiplier = "1"
# timespan = "minute"

# response = requests.get(
#     f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start}/{end}?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
# ).json()
# data = pd.DataFrame(response["results"])

# save_path = f"data/{ticker}/{multiplier}_{timespan}/from_{start}_to_{end}.csv"
