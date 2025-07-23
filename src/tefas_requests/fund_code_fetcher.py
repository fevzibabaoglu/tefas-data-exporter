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


import requests


class FundCodeFetcher:
    URL = "https://www.tefas.gov.tr/api/DB/BindComparisonManagementFees"
    HEADERS = {
        "Content-Length": "23",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.tefas.gov.tr"
    }
    PAYLOAD = {
        "fontip": "YAT",
        "islemdurum": "1"
    }

    def fetch_sorted_fund_codes(self) -> list:
        response = requests.post(self.URL, headers=self.HEADERS, data=self.PAYLOAD)
        response.raise_for_status()

        data = response.json().get("data", [])
        fund_codes = sorted(item["FONKODU"] for item in data if "FONKODU" in item)

        return fund_codes
