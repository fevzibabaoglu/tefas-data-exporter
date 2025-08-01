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
from dateutil.relativedelta import relativedelta
from enum import Enum

from .utils import Utils


class DateRange:
    def __init__(self, start_date: date, end_date: date):
        self.start_date = start_date
        self.end_date = end_date
        self._check_validity()

    def get_start_date(self) -> date:
        return self.start_date

    def get_end_date(self) -> date:
        return self.end_date
    
    def to_dict(self) -> dict:
        return {
            "start_date": Utils.format_date(self.get_start_date()),
            "end_date": Utils.format_date(self.get_end_date()),
        }

    @classmethod
    def from_dict(cls, data: dict):
        start_date_str = data.get("start_date", None)
        end_date_str = data.get("end_date", None)

        return cls(
            start_date=Utils.parse_date(start_date_str) if start_date_str else None,
            end_date=Utils.parse_date(end_date_str) if end_date_str else None,
        )

    def _check_validity(self) -> bool:
        if not self.get_start_date():
            raise ValueError("Start date cannot be empty.")
        if not isinstance(self.get_start_date(), date):
            raise ValueError("Start date must be an instance of the date class.")
        if not self.get_end_date():
            raise ValueError("End date cannot be empty.")
        if not isinstance(self.get_end_date(), date):
            raise ValueError("End date must be an instance of the date class.")
        if self.get_start_date() > self.get_end_date():
            raise ValueError("Start date must be before end date.")
        return True


class TimeFrame(Enum):
    DAYS = 0
    WEEKS = 1
    MONTHS = 2
    YEARS = 3

    @staticmethod
    def get_date_range(time_frame: 'TimeFrame', time_amount: int, end_date: date) -> DateRange:
        start_date = None

        if time_frame == TimeFrame.DAYS:
            start_date = end_date - relativedelta(days=time_amount)
        elif time_frame == TimeFrame.WEEKS:
            start_date = end_date - relativedelta(weeks=time_amount)
        elif time_frame == TimeFrame.MONTHS:
            start_date = end_date - relativedelta(months=time_amount)
        elif time_frame == TimeFrame.YEARS:
            start_date = end_date - relativedelta(years=time_amount)
        else:
            raise ValueError("Invalid time frame.")

        return DateRange(start_date, end_date)
