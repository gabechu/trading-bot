import os

import pandas as pd
import requests

from src.backend.utils import create_directory

POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")


def download_data(ticker: str) -> pd.DataFrame:
    start = "2021-05-01"
    end = "2022-05-01"
    multiplier = "1"
    timespan = "minute"

    response = requests.get(
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start}/{end}?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
    ).json()
    data = pd.DataFrame(response["results"])

    save_path = f"data/{ticker}/{multiplier}_{timespan}/from_{start}_to_{end}.csv"
    create_directory(save_path)
    data.to_csv(save_path)
    return data
