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
import numpy as np
import pandas as pd
from typing import List, Optional


from .asset_distribution import AssetDistribution
from .date_range import DateRange
from .price import Price


class Asset:
    def __init__(
        self,
        code: str,
        name: str,
        category: str,
        risk_score: int,
        is_in_tefas: bool,
        prices: List[Price],
        asset_distributions: List[AssetDistribution],
    ):
        self.code = code
        self.name = name
        self.category = category
        self.risk_score = risk_score
        self._is_in_tefas = is_in_tefas
        self.asset_distributions = asset_distributions
        self.prices = prices
        self._check_validity()

        self.date_range = DateRange(
            start_date=prices[0].get_date(),
            end_date=prices[-1].get_date(),
        )

    def get_code(self) -> str:
        return self.code

    def get_name(self) -> str:
        return self.name

    def get_category(self) -> str:
        return self.category

    def get_risk_score(self) -> int:
        return self.risk_score

    def is_in_tefas(self) -> bool:
        return self._is_in_tefas

    def get_asset_distributions(self) -> List[AssetDistribution]:
        return self.asset_distributions
    
    def get_last_price(self) -> Price:
        return self.get_prices()[-1]

    def get_prices(self, date_range: Optional[DateRange] = None) -> List[Price]:
        if date_range is None:
            return self.prices

        return [
            p for p in self.prices
            if date_range.get_start_date() <= p.get_date() <= date_range.get_end_date()
        ]

    def get_price_change_ratio(self, date_range: Optional[DateRange] = None) -> float:
        if date_range is None:
            start_price = self.prices[0].get_value()
            end_price = self.prices[-1].get_value()
        else:
            filtered_prices = self.get_prices(date_range)
            start_price = filtered_prices[0].get_value()
            end_price = filtered_prices[-1].get_value()

        return round(end_price / start_price - 1, 4)

    def get_date_range(self) -> DateRange:
        return self.date_range

    def to_dict(self) -> dict:
        return {
            "code": self.get_code(),
            "name": self.get_name(),
            "category": self.get_category(),
            "risk_score": self.get_risk_score(),
            "is_in_tefas": self.is_in_tefas(),
            "prices": [price.to_dict() for price in self.get_prices()],
            "asset_distributions": [dist.to_dict() for dist in self.get_asset_distributions()],
            "date_range": self.get_date_range().to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Asset':
        price_dicts = data.get("prices", None)
        prices = [
            Price.from_dict(price)
            for price in price_dicts
        ] if price_dicts else None

        asset_distribution_dicts = data.get("asset_distributions", None)
        asset_distributions = [
            AssetDistribution.from_dict(dist)
            for dist in asset_distribution_dicts
        ] if asset_distribution_dicts else None

        return cls(
            code=data.get("code", None),
            name=data.get("name", None),
            category=data.get("category", None),
            risk_score=data.get("risk_score", None),
            is_in_tefas=data.get("is_in_tefas", None),
            prices=prices,
            asset_distributions=asset_distributions,
        )

    @classmethod
    def from_csv(cls, csv_path: str) -> List['Asset']:
        def _parse_to_list(x):
            if isinstance(x, str):
                try:
                    return ast.literal_eval(x)
                except (ValueError, SyntaxError):
                    return x
            return x

        df = pd.read_csv(csv_path, encoding="utf-8")

        for col in df.columns:
            df[col] = df[col].apply(_parse_to_list)
        df = df.replace({np.nan: None})

        return [
            cls.from_dict(row)
            for row in df.to_dict(orient="records")
        ]

    def _check_validity(self) -> bool:
        if not self.get_code():
            raise ValueError("Asset code cannot be empty.")
        if not isinstance(self.get_code(), str):
            raise ValueError("Asset code must be a string.")
        if not self.get_name():
            raise ValueError("Asset name cannot be empty.")
        if not isinstance(self.get_name(), str):
            raise ValueError("Asset name must be a string.")
        if not self.get_category():
            raise ValueError("Asset category cannot be empty.")
        if not isinstance(self.get_category(), str):
            raise ValueError("Asset category must be a string.")
        if not self.get_risk_score():
            raise ValueError("Asset risk score cannot be empty.")
        if not isinstance(self.get_risk_score(), int):
            raise ValueError("Asset risk score must be an integer.")
        if self.get_risk_score() <= 0:
            raise ValueError("Asset risk score must be a positive integer.")
        if self.is_in_tefas() is None:
            raise ValueError("Asset TEFAS status cannot be None.")
        if not isinstance(self.is_in_tefas(), bool):
            raise ValueError("Asset TEFAS status must be a boolean.")
        if not self.get_prices():
            raise ValueError("Prices cannot be empty.")
        if not isinstance(self.get_prices(), list):
            raise ValueError("Prices must be a list.")
        if not all(isinstance(price, Price) for price in self.get_prices()):
            raise ValueError("All prices must be instances of the Price class.")
        if not self.get_asset_distributions():
            raise ValueError("Asset distributions cannot be empty.")
        if not isinstance(self.get_asset_distributions(), list):
            raise ValueError("Asset distributions must be a list.")
        if not all(isinstance(dist, AssetDistribution) for dist in self.get_asset_distributions()):
            raise ValueError("All asset distributions must be instances of the AssetDistribution class.")
        return True
