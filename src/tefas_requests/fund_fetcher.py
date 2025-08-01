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


import re
from typing import Optional, Union, List

from .tefas_requester import TEFASRequester
from data_struct import AssetDistribution, Asset, Price, Utils


class FundFetcher:
    URL_ENDPOINT = "FonAnaliz.aspx?FonKod={code}"

    TRANSLATION_MAIN_INDICATORS = {
        "Kategorisi": "category",
    }


    def __init__(self, code):
        self.code = code
        self.soup = TEFASRequester.get_soup(
            self.URL_ENDPOINT.format(code=self.code),
            timeout=5,
        )

    def extract_main_indicators(self) -> dict:
        main_div = self.soup.find('div', class_='main-indicators')
        if not main_div:
            return {}

        data = {}

        fund_name_tag = main_div.find('span', id='MainContent_FormViewMainIndicators_LabelFund')
        if fund_name_tag:
            data['name'] = fund_name_tag.text.strip()

        for li in main_div.find(attrs={'class': 'top-list'}).find_all('li'):
            strings = list(li.stripped_strings)
            if not strings:
                continue

            key = strings[0]
            translated = self.TRANSLATION_MAIN_INDICATORS.get(key, None)
            if not translated:
                continue

            value = strings[1] if len(strings) >= 2 else None
            data[translated] = self._clean_main_indicator_value(value)

        return data

    def extract_fund_risk_score(self) -> int:
        profile_table = self.soup.find('div', class_='fund-profile').find('table', id='MainContent_DetailsViewFund')
        if not profile_table:
            return -1

        for row in profile_table.find_all('tr'):
            header = row.find('td', class_='fund-profile-header')
            item = row.find('td', class_='fund-profile-item')
            if header and item and header.get_text(strip=True) == "Fonun Risk Değeri":
                risk_score = item.get_text(strip=True)
                if risk_score.isdigit():
                    return int(risk_score)

        return -1

    def extract_chart_data(self) -> List[Price]:
        scripts = "".join(str(tag) for tag in self.soup.find_all('script', type='text/javascript'))

        match = re.search(
            r"chartMainContent_FonFiyatGrafik.*?xAxis.*?categories.*?\[(.*?)\].*?series.*?data.*?\[(.*?)\]",
            scripts, re.DOTALL
        )
        if not match:
            return []

        dates = [self._clean_price_chart_value(d) for d in match.group(1).split(',')]
        prices = [self._clean_price_chart_value(p) for p in match.group(2).split(',')]

        price_list = [
            Price(
                date=Utils.parse_date(d),
                value=p,
            )
            for d, p in zip(dates, prices)
        ]
        return price_list

    def extract_asset_distribution(self) -> List[AssetDistribution]:
        scripts = "".join(str(tag) for tag in self.soup.find_all('script', type='text/javascript'))

        match = re.search(
            r"chartMainContent_PieChartFonDagilim.*?series.*?data.*?\[(.*?)\],[^\]]*?showInLegend",
            scripts, re.DOTALL
        )
        if not match:
            return []

        asset_pairs = re.findall(r'\["(.*?)",([\d.]+)\]', match.group(1))
        distribution = [(asset, self._clean_distribution_value(percent)) for asset, percent in asset_pairs]
        distribution.sort(key=lambda x: x[1], reverse=True)

        distribution_list = [
            AssetDistribution(
                distribution_name=asset,
                distribution_amount=amount / 100,
            )
            for asset, amount in distribution
        ]
        return distribution_list

    def get_fund_data(self) -> Asset:
        main_indicators = self.extract_main_indicators()
        risk_score = self.extract_fund_risk_score()
        prices = self.extract_chart_data()
        asset_distribution = self.extract_asset_distribution()

        asset = Asset(
            code=self.code,
            name=main_indicators.get('name', ''),
            category=main_indicators.get('category', ''),
            risk_score=risk_score,
            prices=prices,
            asset_distributions=asset_distribution,
        )
        return asset

    @staticmethod
    def _clean_main_indicator_value(value: str) -> Optional[Union[str]]:
        if not value:
            return None

        cleaned_value = value.strip().replace('.', '').replace(',', '.').strip('%')

        try:
            return float(cleaned_value)
        except ValueError:
            pass

        return cleaned_value

    @staticmethod
    def _clean_price_chart_value(value: str) -> Optional[Union[str, float]]:
        if not value:
            return None

        cleaned_value = value.strip().strip('"').strip("'")

        try:
            return float(cleaned_value)
        except ValueError:
            pass

        return cleaned_value

    @staticmethod
    def _clean_distribution_value(value: str) -> Optional[Union[str, float]]:
        if not value:
            return None

        try:
            return float(value)
        except ValueError:
            pass

        return value
