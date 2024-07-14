import os
from enum import Enum

import pandas as pd
import pandera as pa
import requests
import yfinance as yf
from dotenv import load_dotenv
from pandera import Check, Column, DataFrameSchema

from src.utils import create_directory


class TimeSpan(str, Enum):
    MINUTE = "minute"
    # Add other time spans as needed


class YahooEtfSchema:
    schema = DataFrameSchema(
        {
            "Open": Column(float, Check(lambda s: s >= 0)),
            "High": Column(float, Check(lambda s: s >= 0)),
            "Low": Column(float, Check(lambda s: s >= 0)),
            "Close": Column(float, Check(lambda s: s >= 0)),
            "Volume": Column(int, Check(lambda s: s >= 0)),
            "Dividends": Column(float, Check(lambda s: s >= 0)),
            "Stock Splits": Column(float, Check(lambda s: s >= 0)),
            "Capital Gains": Column(float, Check(lambda s: s >= 0)),
        },
        index=pa.Index(pa.DateTime, name="Date"),
    )

    @classmethod
    def validate(cls, data: pd.DataFrame) -> pd.DataFrame:
        return cls.schema.validate(data)


class YahooSecuritySchema:
    schema = DataFrameSchema(
        {
            "Open": Column(float, Check(lambda s: s >= 0)),
            "High": Column(float, Check(lambda s: s >= 0)),
            "Low": Column(float, Check(lambda s: s >= 0)),
            "Close": Column(float, Check(lambda s: s >= 0)),
            "Volume": Column(int, Check(lambda s: s >= 0)),
            "Dividends": Column(float, Check(lambda s: s >= 0)),
            "Stock Splits": Column(float, Check(lambda s: s >= 0)),
        },
        index=pa.Index(pa.DateTime, name="Date"),
    )

    @classmethod
    def validate(cls, data: pd.DataFrame) -> pd.DataFrame:
        return cls.schema.validate(data)


class DataLoader:
    def __init__(self):
        load_dotenv()
        self._polygon_api_key = os.environ.get("POLYGON_API_KEY")

    def load_data_from_yahoo(self, ticker: str, period: str = "2y") -> pd.DataFrame:
        data = yf.Ticker(ticker).history(period=period)
        data.index = data.index.tz_convert("UTC").tz_localize(None)

        if "Capital Gains" in data.columns:
            validated_data = YahooEtfSchema.validate(data)
        else:
            validated_data = YahooSecuritySchema.validate(data)

        return validated_data.dropna().sort_index()

    def load_data_from_polygon(
        self, ticker: str, start: str, end: str, multiplier: int, timespan: TimeSpan
    ) -> pd.DataFrame:
        response = requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan.value}/{start}/{end}?adjusted=true&sort=asc&apiKey={self._polygon_api_key}"
        ).json()
        return pd.DataFrame(response["results"])

    def download_data(self, data: pd.DataFrame, save_path: str) -> pd.DataFrame:
        create_directory(save_path)
        data.to_csv(save_path)
        return data
