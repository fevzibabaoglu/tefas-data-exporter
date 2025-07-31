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


import pandas as pd
from typing import List

from data_struct import Asset, TimeFrame


class DataProcessor:
    pd.set_option('future.no_silent_downcasting', True)

    PRICE_CHANGE_COLUMNS = [
        {"time_frame": TimeFrame.DAYS, "amount": 1},
        {"time_frame": TimeFrame.DAYS, "amount": 2},
        {"time_frame": TimeFrame.DAYS, "amount": 3},
        {"time_frame": TimeFrame.WEEKS, "amount": 1},
        {"time_frame": TimeFrame.WEEKS, "amount": 2},
        {"time_frame": TimeFrame.WEEKS, "amount": 3},
        {"time_frame": TimeFrame.MONTHS, "amount": 1},
        {"time_frame": TimeFrame.MONTHS, "amount": 2},
        {"time_frame": TimeFrame.MONTHS, "amount": 3},
        {"time_frame": TimeFrame.MONTHS, "amount": 4},
        {"time_frame": TimeFrame.MONTHS, "amount": 5},
        {"time_frame": TimeFrame.MONTHS, "amount": 6},
        {"time_frame": TimeFrame.MONTHS, "amount": 9},
        {"time_frame": TimeFrame.YEARS, "amount": 1},
    ]


    def __init__(self, assets: List[Asset]):
        self.assets = assets

    def process(self) -> pd.DataFrame:
        price_df = self._parse_price_change_ratios()
        dist_df = self._parse_asset_distribution()

        df = pd.DataFrame({
            'code': [asset.get_code() for asset in self.assets],
        })
        df = pd.concat([df, price_df], axis=1)
        df = pd.concat([df, dist_df], axis=1)

        return df

    def _parse_price_change_ratios(self):
        price_change_ratios = []

        for asset in self.assets:
            asset_price_change = {}

            for change in self.PRICE_CHANGE_COLUMNS:
                time_frame = change["time_frame"]
                amount = change["amount"]

                asset_start_date = asset.get_date_range().get_start_date()
                asset_end_date = asset.get_date_range().get_end_date()
                date_range = TimeFrame.get_date_range(time_frame, amount, asset_end_date)

                if asset_start_date > date_range.get_start_date():
                    continue

                price_change = asset.get_price_change_ratio(date_range)
                asset_price_change[f"{time_frame.name.lower()}_{amount}"] = price_change

            price_change_ratios.append(asset_price_change)

        return pd.DataFrame(price_change_ratios)

    def _parse_asset_distribution(self):
        asset_distributions_list = []

        for asset in self.assets:
            asset_distribution_dict = {}

            for distribution in asset.get_asset_distributions():
                asset_distribution_dict[distribution.get_distribution_name()] = distribution.get_distribution_amount()

            asset_distributions_list.append(asset_distribution_dict)

        df = pd.DataFrame(asset_distributions_list)
        df = df[sorted(col for col in df.columns if col != 'Diğer') + ['Diğer']]
        return df
