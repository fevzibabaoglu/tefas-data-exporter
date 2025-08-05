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

from utils import DateUtils


class Price:
    def __init__(self, date: date, value: float):
        self.date = date
        self.value = value
        self._check_validity()

    def get_date(self) -> date:
        return self.date

    def get_value(self) -> float:
        return self.value

    def set_value(self, value: float):
        self.value = value
        self._check_validity()

    def to_dict(self) -> dict:
        return {
            "date": DateUtils.format_date(self.get_date()),
            "value": self.get_value(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        date_str = data.get("date", None)
        value_str = data.get("value", None)

        return cls(
            date=DateUtils.parse_date(date_str) if date_str else None,
            value=float(value_str) if value_str else None,
        )

    def _check_validity(self) -> bool:
        if not self.get_date():
            raise ValueError("Date cannot be empty.")
        if not isinstance(self.get_date(), date):
            raise ValueError("Date must be instance of the date class.")
        if not self.get_value():
            raise ValueError("Price value cannot be empty.")
        if not isinstance(self.get_value(), float):
            raise ValueError("Price value must be a float number.")
        if self.get_value() < 0:
            raise ValueError("Price value cannot be negative.")
        return True
