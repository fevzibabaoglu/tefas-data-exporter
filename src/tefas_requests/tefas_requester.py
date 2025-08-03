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


import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
from typing import Optional


class TEFASRequester:
    BASE_URL = "https://www.tefas.gov.tr"
    BASE_HEADERS = {
        'host': 'www.tefas.gov.tr',
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    RETRIES = 5
    DELAY = 0.5

    @staticmethod
    def get_soup(response: requests.Response) -> BeautifulSoup:
        return BeautifulSoup(response.text, 'html.parser')

    @staticmethod
    def get_request(url_endpoint: str, headers: dict = {}, *args, **kwargs) -> requests.Response:
        return TEFASRequester._request("GET", url_endpoint, headers=headers, *args, **kwargs)

    @staticmethod
    def post_request(url_endpoint: str, headers: dict = {}, data: dict = {}, *args, **kwargs) -> requests.Response:
        encoded_str = urllib.parse.urlencode(data)
        encoded_bytes = encoded_str.encode('utf-8')
        content_length = len(encoded_bytes)
        headers.update({"Content-Length": str(content_length)})
        return TEFASRequester._request("POST", url_endpoint, headers=headers, data=data, *args, **kwargs)

    @staticmethod
    def postback_request(url_endpoint: str, headers: dict = {}, form_data: dict = {}, *args, **kwargs) -> requests.Response:
        with requests.Session() as session:
            session.headers.update({**TEFASRequester.BASE_HEADERS, **headers})

            response = TEFASRequester._request_with_session(
                session, "GET", url_endpoint, *args, **kwargs,
            )
            soup = TEFASRequester.get_soup(response)

            # Postback form data
            data = {}

            # Find all <input> tags and extract their name and value
            for input_tag in soup.find_all('input'):
                name = input_tag.get('name')
                if name:
                    data[name] = input_tag.get('value', '')

            # Find <select> tags if any exist
            for select_tag in soup.find_all('select'):
                name = select_tag.get('name')
                selected_option = select_tag.find('option', selected=True)
                if name and selected_option:
                    data[name] = selected_option.get('value', '')

            form_data = {**data, **form_data}
            return TEFASRequester._request_with_session(
                session, "POST", url_endpoint, data=form_data, *args, **kwargs,
            )

    @staticmethod
    def _request(method: str, url_endpoint: str, headers: dict = {}, data: Optional[dict] = None, *args, **kwargs) -> requests.Response:
        with requests.Session() as session:
            session.headers.update({**TEFASRequester.BASE_HEADERS, **headers})
            return TEFASRequester._request_with_session(
                session, method, url_endpoint, headers=headers, data=data, *args, **kwargs,
            )

    @staticmethod
    def _request_with_session(
        session: requests.Session,
        method: str,
        url_endpoint: str,
        data: Optional[dict] = None,
        *args, **kwargs,
    ) -> requests.Response:
        url = f"{TEFASRequester.BASE_URL}/{url_endpoint}"

        for attempt in range(TEFASRequester.RETRIES):
            try:
                response = session.request(method, url, data=data, *args, **kwargs)
                response.raise_for_status()
                return response
            except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
                if attempt < TEFASRequester.RETRIES - 1:
                    time.sleep(TEFASRequester.DELAY * (attempt + 1))
                else:
                    raise e
