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
from typing import List, Dict

from data_struct import Asset
from tefas_requests import FundAnalyzer, FundCodeFetcher


class FundDataManager:
    def __init__(
        self,
        fund_code_fetcher: FundCodeFetcher,
        include_price_chart: bool = False,
        max_workers: int = 16,
    ):
        self.fund_code_fetcher = fund_code_fetcher
        self.include_price_chart = include_price_chart
        self.max_workers = max_workers

        self.lock = threading.Lock()
        self.data: List[Dict] = []

    def fetch_all_fund_data(self) -> List[Asset]:
        fund_codes = self.fund_code_fetcher.fetch_sorted_fund_codes()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_and_store, code): code
                for code in fund_codes
            }

            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching funds", unit="fund"):
                code = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error fetching fund {code}: {e}")

        return self.data

    def _fetch_and_store(self, code: str) -> None:
        analyzer = FundAnalyzer(code)
        asset = analyzer.get_fund_data()

        with self.lock:
            self.data.append(asset)
