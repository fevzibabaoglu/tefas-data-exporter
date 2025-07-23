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
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, Union


class FundAnalyzer:
    BASE_URL = "https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={code}"
    HEADERS = {
        'host': 'www.tefas.gov.tr'
    }

    TRANSLATION_MAIN_INDICATORS = {
        "Son Fiyat (TL)": "last_price",
        "Günlük Getiri (%)": "1_day",
        "Kategorisi": "category",
    }

    TRANSLATION_PRICE_INDICATORS = {
        "Son 1 Ay Getirisi": "1_month",
        "Son 3 Ay Getirisi": "3_month",
        "Son 6 Ay Getirisi": "6_month",
        "Son 1 Yıl Getirisi": "1_year"
    }

    EARNINGS_INTERVALS = {
        "2_day": timedelta(days=2),
        "3_day": timedelta(days=3),
        "7_day": timedelta(days=7),
        "14_day": timedelta(days=14),
        "21_day": timedelta(days=21),
        "2_month": relativedelta(months=2),
        "4_month": relativedelta(months=4),
        "5_month": relativedelta(months=5),
        "9_month": relativedelta(months=9),
    }


    def __init__(self, code):
        self.code = code
        self.url = self.BASE_URL.format(code=self.code)
        self.soup = self.get_soup()

    def get_soup(self) -> BeautifulSoup:
        retries = 3
        delay = 0.5

        for attempt in range(retries):
            try:
                response = requests.get(self.url, headers=self.HEADERS, timeout=5)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
                else:
                    raise e

    def extract_main_indicators(self) -> dict:
        data = {}
        main_div = self.soup.find('div', class_='main-indicators')
        if not main_div:
            return data

        fund_name_tag = main_div.find('span', id='MainContent_FormViewMainIndicators_LabelFund')
        if fund_name_tag:
            data['name'] = fund_name_tag.text.strip()

        for li in main_div.find(attrs={'class': 'top-list'}).find_all('li'):
            strings = list(li.stripped_strings)
            if not strings:
                continue

            key = strings[0]
            translated = self.TRANSLATION_MAIN_INDICATORS.get(key)
            if not translated:
                continue

            value = strings[1] if len(strings) >= 2 else None
            data[translated] = self._clean_value(value)

        return data

    def extract_price_indicators(self) -> dict:
        data = {}
        price_div = self.soup.find('div', class_='price-indicators')
        if not price_div:
            return data

        for li in price_div.find_all('li'):
            strings = list(li.stripped_strings)
            if not strings:
                continue

            key = strings[0]
            translated = self.TRANSLATION_MAIN_INDICATORS.get(key)
            if not translated:
                continue

            value = strings[1] if len(strings) >= 2 else None
            data[translated] = self._clean_value(value)

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
                return int(risk_score) if risk_score.isdigit() else -1
        return -1

    def extract_chart_data(self) -> list:
        scripts = "".join(str(tag) for tag in self.soup.find_all('script', type='text/javascript'))

        match = re.search(
            r"chartMainContent_FonFiyatGrafik.*?xAxis.*?categories.*?\[(.*?)\].*?series.*?data.*?\[(.*?)\]",
            scripts, re.DOTALL
        )
        if not match:
            return []

        dates = [d.strip().strip('"').strip("'") for d in match.group(1).split(',')]
        prices = [self._clean_value(p) for p in match.group(2).split(',')]
        return list(zip(dates, prices))

    def extract_asset_distribution(self) -> list:
        scripts = "".join(str(tag) for tag in self.soup.find_all('script', type='text/javascript'))

        match = re.search(
            r"chartMainContent_PieChartFonDagilim.*?series.*?data.*?\[(.*?)\],[^\]]*?showInLegend",
            scripts, re.DOTALL
        )
        if not match:
            return []

        asset_pairs = re.findall(r'\["(.*?)",([\d.]+)\]', match.group(1))
        distribution = [(asset, self._clean_value(percent)) for asset, percent in asset_pairs]
        distribution.sort(key=lambda x: x[1], reverse=True)
        return distribution

    def calculate_earnings(self, price_chart: list) -> dict:
        if not price_chart:
            return {}

        latest_date = datetime.strptime(price_chart[-1][0], "%d.%m.%Y").date()
        latest_price = price_chart[-1][1]

        dated_prices = []
        for date_str, price in price_chart:
            try:
                date = datetime.strptime(date_str, "%d.%m.%Y").date()
                dated_prices.append((date, price))
            except ValueError:
                continue

        earnings = {}
        for label, delta in self.EARNINGS_INTERVALS.items():
            target = latest_date - delta
            entry = next(((d, p) for d, p in dated_prices if d >= target), None)
            try:
                _, price = entry
                earnings[label] = round(((latest_price - price) / price) * 100, 6)
            except Exception:
                earnings[label] = None

        return earnings

    def get_fund_data(self, include_price_chart: bool = False) -> dict:
        price_chart = self.extract_chart_data()
        main_indicators = self.extract_main_indicators()
        price_indicators = self.extract_price_indicators()
        calculated_earnings = self.calculate_earnings(price_chart)

        # Merge price change metrics
        price_change = {**price_indicators, **calculated_earnings}
        if '1_day' in main_indicators:
            price_change['1_day'] = main_indicators.pop('1_day')

        data = {
            "code": self.code,
            **main_indicators,
            "risk_score": self.extract_fund_risk_score(),
            "price_change_percentage": price_change,
            "asset_distribution": self.extract_asset_distribution(),
        }

        if include_price_chart:
            data["price_chart"] = price_chart

        return data

    @staticmethod
    def _clean_value(value: str) -> Optional[Union[float, str]]:
        if value is None:
            return None

        cleaned_value = value.replace(',', '.').strip('%').strip()
        try:
            return float(cleaned_value)
        except ValueError:
            return cleaned_value
