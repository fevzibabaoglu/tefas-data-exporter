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


from datetime import date
from typing import Dict, List

from .tefas_requester import TEFASRequester
from data_struct import DateRange, Price
from utils import DateUtils


class UpdatedPricesFetcher:
    URL_ENDPOINT = "api/DB/BindHistoryInfo"
    PAYLOAD = {
        "fontip": "YAT",
        "bastarih": "{start_date}",
        "bittarih": "{end_date}",
    }


    @staticmethod
    def fetch_updated_prices(date_range: DateRange) -> Dict[str, List[Price]]:
        data = {}

        for fetch_date in date_range.get_all_dates():
            payload = UpdatedPricesFetcher._format_payload(fetch_date, fetch_date)
            response = TEFASRequester.post_request(UpdatedPricesFetcher.URL_ENDPOINT, data=payload)
            response_data = response.json().get("data", [])

            for item in response_data:
                fund_code = item.get("FONKODU", None)
                price_str = item.get("FIYAT", "0.0")

                price_float = float(price_str)
                if price_float == 0.0:
                    continue

                price = Price(
                    date=fetch_date,
                    value=price_float
                )
                data.setdefault(fund_code, []).append(price)

        return data

    @staticmethod
    def _format_payload(start_date: date, end_date: date) -> dict:
        return {
            key: v.format(
                start_date=DateUtils.format_date(start_date),
                end_date=DateUtils.format_date(end_date),
            )
            for key, v in UpdatedPricesFetcher.PAYLOAD.items()
        }
