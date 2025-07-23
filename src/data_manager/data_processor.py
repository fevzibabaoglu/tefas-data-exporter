"""
tefas-data-exporter - Export raw data from TEFAS website.
Copyright (C) 2025  Fevzi Babaoğlu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import ast
import pandas as pd


class DataProcessor:
    pd.set_option('future.no_silent_downcasting', True)


    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def process(self) -> pd.DataFrame:
        price_df = self._parse_price_change()
        dist_df = self._parse_asset_distribution()

        self.df.drop(columns=["price_change_percentage", "asset_distribution"], inplace=True)
        self.df = pd.concat([self.df, price_df], axis=1)
        self.df = pd.concat([self.df, dist_df], axis=1)

        # Replace placeholders with pd.NA (empty cell)
        self.df.replace(to_replace=[0, 0.0, ""], value=pd.NA, inplace=True)
        self.df["risk_score"] = self.df["risk_score"].replace(-1, pd.NA)

        return self.df

    def _parse_price_change(self):
        def _safe_eval_to_series(x):
            if isinstance(x, dict):
                return pd.Series(x)
            elif isinstance(x, str):
                try:
                    return pd.Series(ast.literal_eval(x))
                except Exception:
                    return pd.Series()
            else:
                return pd.Series()

        price_df = self.df["price_change_percentage"].apply(_safe_eval_to_series)

        # Sort price columns
        price_order = [
            "1_day", "2_day", "3_day", "7_day", "14_day", "21_day",
            "1_month", "2_month", "3_month", "4_month", "5_month", "6_month", "9_month",
            "1_year"
        ]
        return price_df[[col for col in price_order if col in price_df.columns]]

    def _parse_asset_distribution(self):
        def _safe_parse_distribution(x):
            if isinstance(x, list):
                return dict(x)
            elif isinstance(x, str):
                try:
                    return dict(ast.literal_eval(x))
                except Exception:
                    return {}
            else:
                return {}

        dist_series = self.df["asset_distribution"].apply(_safe_parse_distribution)

        # Turn each list of tuples into a dict: {"Asset": value, ...}
        dist_dicts = dist_series.apply(lambda lst: dict(lst))

        dist_df = dist_dicts.apply(pd.Series).fillna(0)
        dist_df = dist_df[sorted(dist_df.columns)]
        return dist_df
