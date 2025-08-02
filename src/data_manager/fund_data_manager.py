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


import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import List, Dict, Optional

from data_struct import Asset, Founder
from tefas_requests import FundFetcher, FundCodeFetcher


class FundDataManager:
    def __init__(
        self,
        include_price_chart: bool = False,
        max_workers: int = 16,
        additional_founders: Optional[List[Founder]] = None,
    ):
        self.include_price_chart = include_price_chart
        self.max_workers = max_workers
        self.additional_founders = additional_founders

        self.lock = threading.Lock()
        self.data: List[Dict] = []

    def fetch_all_fund_data(self) -> List[Asset]:
        fund_codes_data = FundCodeFetcher.fetch_tefas_fund_codes()

        if self.additional_founders:
            existing_codes = {data['fund_code'] for data in fund_codes_data}

            for founder in self.additional_founders:
                codes = FundCodeFetcher.fetch_founder_fund_codes(founder)

                for code in codes:
                    if code['fund_code'] not in existing_codes:
                        fund_codes_data.append(code)
                        existing_codes.add(code['fund_code'])

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_fund_data, data['fund_code'], data['founder']): data['fund_code']
                for data in fund_codes_data
            }

            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching funds", unit="fund"):
                code = futures[future]
                try:
                    future.result()
                except Exception as e:
                    tqdm.write(f"Error fetching fund {code}: {e}")

        return self.data

    def _fetch_fund_data(self, code: str, founder: Founder) -> None:
        analyzer = FundFetcher(code, founder)
        asset = analyzer.get_fund_data()

        with self.lock:
            self.data.append(asset)
