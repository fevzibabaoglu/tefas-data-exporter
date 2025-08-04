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


class AssetDistribution:
    def __init__(self, distribution_name: str, distribution_amount: float):
        self.distribution_name = distribution_name
        self.distribution_amount = distribution_amount
        self._check_validity()

    def get_distribution_name(self) -> str:
        return self.distribution_name

    def get_distribution_amount(self) -> float:
        return round(self.distribution_amount, 4)

    def to_dict(self) -> dict:
        return {
            "name": self.get_distribution_name(),
            "amount": self.get_distribution_amount()
        }

    @classmethod
    def from_dict(cls, data: dict):
        name_str = data.get("name", None)
        amount_str = data.get("amount", None)

        return cls(
            distribution_name=name_str,
            distribution_amount=float(amount_str) if amount_str else None
        )

    def _check_validity(self) -> bool:
        if not self.get_distribution_name():
            raise ValueError("Distribution name cannot be empty.")
        if not isinstance(self.get_distribution_name(), str):
            raise ValueError("Distribution name must be a string.")
        if not self.get_distribution_amount():
            raise ValueError("Distribution amount cannot be empty.")
        if not isinstance(self.get_distribution_amount(), float):
            raise ValueError("Distribution amount must be a float number.")
        if self.get_distribution_amount() == 0.0:
            raise ValueError("Distribution amount cannot be zero.")
        return True
