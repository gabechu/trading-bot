from functools import cached_property

import pandas as pd

from src.data_loader import DataLoader


class Portfolio:
    def __init__(self, tickers: list[str], weights: list[float], timeframe: str):
        if sum(weights) != 1:
            raise ValueError("Weights must sum to 1")
        if len(weights) != len(tickers):
            raise ValueError("The length of weights must match the number of columns in the combined DataFrame")

        self._tickers = tickers
        self._weights = weights
        self._timeframe = timeframe
        self._data_loader = DataLoader()

    @cached_property
    def data(self) -> dict[str, pd.DataFrame]:
        return {ticket: self._data_loader.load_data_from_yahoo(ticket, self._timeframe) for ticket in self._tickers}

    def _combine_close_columns(self) -> pd.DataFrame:
        close_dfs = []
        for ticker, df in self.data.items():
            close_df = df[["Close"]].copy()
            close_df.columns = pd.Index([f"Close_{ticker}"])

            # Normalize the Date index to remove the time component
            if isinstance(close_df.index, pd.DatetimeIndex):
                close_df.index = close_df.index.normalize()
            else:
                raise TypeError("Index must be a DatetimeIndex")

            close_dfs.append(close_df)

        combined_close_df = pd.concat(close_dfs, axis=1, join="inner")
        return combined_close_df

    def _calculate_portfolio_value(self, combined_df: pd.DataFrame) -> pd.Series:
        return (combined_df * self._weights).sum(axis=1)

    def calculate_max_drawdown(self):
        combined_df = self._combine_close_columns()
        portfolio_value = self._calculate_portfolio_value(combined_df)

        cumulative_max = portfolio_value.cummax()

        # Calculate the drawdown
        drawdown = (portfolio_value / cumulative_max) - 1

        max_drawdown = drawdown.min()
        max_drawdown_date = drawdown.idxmin()
        cumulative_max_date = cumulative_max.loc[:max_drawdown_date].idxmax()

        print(f"The maximum drawdown for the portfolio is {max_drawdown:.2%}")
        print(f"The cumulative maximum was reached on {cumulative_max_date.date()}")
        print(f"The maximum drawdown occurred on {max_drawdown_date.date()}")

        return max_drawdown, max_drawdown_date, cumulative_max_date

    def calculate_annual_return(self):
        combined_df = self._combine_close_columns()
        portfolio_value = self._calculate_portfolio_value(combined_df)

        # Calculate daily returns
        daily_returns = portfolio_value.pct_change().dropna()

        # Calculate average daily return
        avg_daily_return = daily_returns.mean()

        # Annualize the return
        trading_days_per_year = 252  # Approximate number of trading days in a year
        annual_return = (1 + avg_daily_return) ** trading_days_per_year - 1

        print(f"The annual return for the portfolio is {annual_return:.2%}")

        return annual_return
