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


class Founder:
    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name
        self._check_validity()

    def get_code(self) -> str:
        return self.code

    def get_name(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {
            "founder_code": self.get_code(),
            "founder_name": self.get_name()
        }

    def _check_validity(self) -> bool:
        if not self.get_code():
            raise ValueError("Code cannot be empty.")
        if not isinstance(self.get_code(), str):
            raise ValueError("Code must be a string.")
        if not self.get_name():
            raise ValueError("Name cannot be empty.")
        if not isinstance(self.get_name(), str):
            raise ValueError("Name must be a string.")
        return True
