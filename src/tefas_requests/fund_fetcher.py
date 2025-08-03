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
import re
from enum import Enum, auto
from typing import Optional, Union, List

from .tefas_requester import TEFASRequester
from data_struct import AssetDistribution, Asset, Founder, Price, Utils


class FundFetcher:
    URL_ENDPOINT = "FonAnaliz.aspx?FonKod={code}"

    TRANSLATION_MAIN_INDICATORS = {
        "Kategorisi": "category",
        "Pazar Payı": "market_share",
    }
    TRANSLATION_FUND_PROFILE = {
        "Fonun Risk Değeri": "risk_score",
        "Platform İşlem Durumu": "is_in_tefas",
    }


    def __init__(self, code: str, founder: Founder):
        self.code = code
        self.founder = founder
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

        for li in main_div.find_all('li'):
            strings = list(li.stripped_strings)
            if not strings:
                continue

            key = strings[0]
            translated = self.TRANSLATION_MAIN_INDICATORS.get(key, None)
            if not translated:
                continue

            value = strings[1] if len(strings) >= 2 else None
            data[translated] = self.ValueParser._parse_value(value, self.ValueParser.MAIN_INDICATOR)

        return data

    def extract_fund_profile(self) -> dict:
        profile_table = self.soup.find('div', class_='fund-profile').find('table', id='MainContent_DetailsViewFund')
        if not profile_table:
            return {}

        data = {}

        for row in profile_table.find_all('tr'):
            header = row.find('td', class_='fund-profile-header')
            item = row.find('td', class_='fund-profile-item')
            if header and item:
                header_translated = self.TRANSLATION_FUND_PROFILE.get(
                    header.get_text(strip=True),
                    None,
                )
                if not header_translated:
                    continue

                value = item.get_text(strip=True)
                data[header_translated] = self.ValueParser._parse_value(value, self.ValueParser.FUND_PROFILE)

        return data

    def extract_chart_data(self) -> List[Price]:
        scripts = "".join(str(tag) for tag in self.soup.find_all('script', type='text/javascript'))

        match = re.search(
            r"chartMainContent_FonFiyatGrafik.*?xAxis.*?categories.*?(\[.*?\]).*?series.*?data.*?(\[.*?\])",
            scripts, re.DOTALL
        )
        if not match:
            return []

        dates = ast.literal_eval(match.group(1))
        prices = ast.literal_eval(match.group(2))

        price_list = [
            Price(
                date=Utils.parse_date(d),
                value=p,
            )
            for d, p in zip(dates, prices)
            if p != 0.0
        ]
        return price_list

    def extract_asset_distribution(self) -> List[AssetDistribution]:
        scripts = "".join(str(tag) for tag in self.soup.find_all('script', type='text/javascript'))

        match_pie = self.AssetDistributionParser._parse_asset_distribution(scripts, self.AssetDistributionParser.PIE)
        match_column = self.AssetDistributionParser._parse_asset_distribution(scripts, self.AssetDistributionParser.COLUMN)

        if match_pie:
            asset_pairs = match_pie
        elif match_column:
            asset_pairs = match_column
        else:
            return []

        distribution = [(asset, percent) for asset, percent in asset_pairs]
        distribution.sort(key=lambda x: x[1], reverse=True)

        distribution_list = [
            AssetDistribution(
                distribution_name=asset,
                distribution_amount=amount / 100,
            )
            for asset, amount in distribution
            if amount != 0.0
        ]
        return distribution_list

    def get_fund_data(self) -> Asset:
        main_indicators = self.extract_main_indicators()
        fund_profile = self.extract_fund_profile()
        prices = self.extract_chart_data()
        asset_distribution = self.extract_asset_distribution()

        market_share = main_indicators.get('market_share', None)
        market_share = market_share / 100 if market_share is not None else None

        asset = Asset(
            code=self.code,
            name=main_indicators.get('name', ''),
            founder=self.founder,
            category=main_indicators.get('category', ''),
            risk_score=fund_profile['risk_score'],
            market_share=market_share,
            is_in_tefas=fund_profile['is_in_tefas'],
            prices=prices,
            asset_distributions=asset_distribution,
        )
        return asset


    class ValueParser(Enum):
        MAIN_INDICATOR = auto()
        FUND_PROFILE = auto()

        @staticmethod
        def _parse_value(value: str, context: "FundFetcher.ValueParser") -> Optional[Union[str, int, float, bool]]:
            if value is None:
                return None

            value = value.strip()
            if value == "":
                return None

            if context == FundFetcher.ValueParser.MAIN_INDICATOR:
                return FundFetcher.ValueParser.__parse_as_main_indicator(value)
            if context == FundFetcher.ValueParser.FUND_PROFILE:
                return FundFetcher.ValueParser.__parse_as_fund_profile(value)

            return value

        @staticmethod
        def __parse_as_main_indicator(value: str) -> Union[float, str]:
            value = value.replace('.', '').replace(',', '.').strip('%')
            try:
                return float(value)
            except ValueError:
                return value

        @staticmethod
        def __parse_as_fund_profile(value: str) -> Union[int, bool, str]:
            value = value.replace('.', '')
            if value.isdigit():
                return int(value)
            if value == "TEFAS'ta işlem görüyor":
                return True
            if value == "TEFAS'ta İşlem Görmüyor":
                return False
            return value


    class AssetDistributionParser(Enum):
        PIE = auto()
        COLUMN = auto()

        @staticmethod
        def _parse_asset_distribution(string: str, type: "FundFetcher.AssetDistributionParser") -> Optional[List]:
            if type == FundFetcher.AssetDistributionParser.PIE:
                return FundFetcher.AssetDistributionParser.__asset_distribution_pie_regex(string)
            elif type == FundFetcher.AssetDistributionParser.COLUMN:
                return FundFetcher.AssetDistributionParser.__asset_distribution_column_regex(string)

        @staticmethod
        def __asset_distribution_pie_regex(string: str) -> Optional[List]:
            match = re.search(
                r"chartMainContent_PieChartFonDagilim.*?series.*?data.*?(\[.*?\]),[^\]]*?showInLegend",
                string, re.DOTALL,
            )
            if not match:
                return None

            match_data = ast.literal_eval(match.group(1))
            return match_data

        @staticmethod
        def __asset_distribution_column_regex(string: str) -> Optional[List]:
            match = re.search(
                r"chartMainContent_ColumnChartFonDagilim.*?series: (\[\{.*?\}\])",
                string, re.DOTALL,
            )
            if not match:
                return None

            match_data = ast.literal_eval(match.group(1))
            asset_pairs = [(item['name'], item['data'][0]) for item in match_data]
            return asset_pairs
