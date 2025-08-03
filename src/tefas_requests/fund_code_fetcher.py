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


from typing import List, Dict, Union

from .tefas_requester import TEFASRequester
from data_struct import Founder


class FundCodeFetcher:
    URL_ENDPOINT = "api/DB/BindComparisonManagementFees"
    PAYLOAD = {
        "fontip": "YAT",
    }

    founders = None


    @classmethod
    def set_founders(cls, founders: List[Founder]) -> None:
        cls.founders = founders


    @staticmethod
    def fetch_tefas_fund_codes() -> List[Dict[str, Union[str, Founder]]]:
        payload = {"islemdurum": "1", **FundCodeFetcher.PAYLOAD}
        return FundCodeFetcher._fetch_fund_codes(payload)

    @staticmethod
    def fetch_founder_fund_codes(founder_code: str) -> List[Dict[str, Union[str, Founder]]]:
        payload = {"kurucukod": founder_code, **FundCodeFetcher.PAYLOAD}
        return FundCodeFetcher._fetch_fund_codes(payload)

    @staticmethod
    def _fetch_fund_codes(payload: dict) -> List[Dict[str, Union[str, Founder]]]:
        response = TEFASRequester.post_request(FundCodeFetcher.URL_ENDPOINT, data=payload)
        response_data = response.json().get("data", [])

        data = []
        for item in response_data:
            fund_code = item.get("FONKODU", None)
            founder_code = item.get("KURUCUKODU", None)

            founder = next((f for f in FundCodeFetcher.founders if f.get_code() == founder_code), None) \
                        if founder_code and FundCodeFetcher.founders \
                        else None

            if fund_code:
                data.append({
                    "fund_code": fund_code,
                    "founder": founder,
                })

        data.sort(key=lambda x: x["fund_code"])
        return data
