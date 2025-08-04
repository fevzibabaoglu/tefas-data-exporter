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


from typing import List

from .tefas_requester import TEFASRequester
from data_struct import Founder


class FounderFetcher:
    URL_ENDPOINT = "FonKarsilastirma.aspx"


    @staticmethod
    def fetch_founders() -> List[Founder]:
        response = TEFASRequester.get_request(FounderFetcher.URL_ENDPOINT, timeout=5)
        soup = TEFASRequester.get_soup(response)
        select = soup.find('select', id='DropDownListFounderYAT')
        options = select.find_all('option')

        founders = []
        for option in options:
            value = option['value']
            name = option.text.strip()

            if value != "Tümü":
                founders.append(Founder(code=value, name=name))

        return founders
