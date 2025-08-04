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


from dateutil.relativedelta import relativedelta
from typing import List

from .fund_data_manager import FundDataManager
from data_struct import Asset, DateRange
from tefas_requests import FundCodeFetcher, UpdatedPricesFetcher
from utils import DateUtils


class PriceUpdater:
    def __init__(self, assets: List[Asset], fund_data_manager: FundDataManager):
        self.code_asset_dict = Asset.get_code_asset_dict(assets)
        self.fund_data_manager = fund_data_manager

    def get_last_date(self):
        return max(
            asset.get_date_range().get_end_date()
            for asset in self.code_asset_dict.values()
        )
    
    def update_prices(self) -> List[Asset]:
        last_date = self.get_last_date()
        date_range = DateRange(
            start_date=last_date + relativedelta(days=1),
            end_date=DateUtils.get_today()
        )

        new_asset_codes = []
        new_asset_prices = UpdatedPricesFetcher.fetch_updated_prices(date_range)
        for fund_code, prices in new_asset_prices.items():
            asset = self.code_asset_dict.get(fund_code, None)
            if asset is not None:
                asset.extend_prices(prices)
            else:
                new_asset_codes.append(fund_code)

        assets = list(self.code_asset_dict.values())

        fund_codes_data = {
            fund_code: founder
            for fund_code, founder in FundCodeFetcher.fetch_tefas_fund_codes().items()
            if fund_code in new_asset_codes
        }
        if fund_codes_data:
            new_assets = self.fund_data_manager.fetch_fund_data(fund_codes_data)
            assets.extend(new_assets)

        return assets
