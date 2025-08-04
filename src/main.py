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


import argparse
import pandas as pd
from pathlib import Path

from data_manager import DataProcessor, FundDataManager, PriceUpdater
from data_struct import Asset
from tefas_requests import FounderFetcher, FundCodeFetcher
from utils import DataFrameUtils


class Main:
    def __init__(
        self,
        raw_csv_filename: str = "fund_data_raw.csv",
        processed_csv_filename: str = "fund_data.csv",
    ):
        self.args = self.parse_args()
        self.raw_csv_filename = raw_csv_filename
        self.processed_csv_filename = processed_csv_filename
        self._parse_args()

        self.input_path = self._parse_input_path()
        self.output_directory_path = self._parse_output_directory_path()
        self.raw_output_path = self._parse_raw_output_path(self.raw_csv_filename)
        self.processed_output_path = self._parse_processed_output_path(self.processed_csv_filename)
        self._check_validity()

        self.founder_data = self.get_founder_data()

    def parse_args(self):
        parser = argparse.ArgumentParser(description="TEFAS Data Exporter")
        parser.add_argument(
            "--input", type=str,
            help="Optional path to a raw fund CSV. If provided, skips fetching real-time data."
        )
        parser.add_argument(
            "--output", type=str, default="output",
            help="Output directory to save the files. (default: 'output')"
        )
        parser.add_argument(
            "--no-processed", action="store_true",
            help="Do not include processed data in the output."
        )
        parser.add_argument(
            "--update", action="store_true",
            help="Update the price data."
        )
        parser.add_argument(
            "--get-only-founders", action="store_true",
            help="Fetch only founder data and display."
        )
        parser.add_argument(
            '--founders', nargs='+', type=str,
            help='List of founder codes for additional fetching.'
        )
        parser.add_argument(
            '--range', type=str,
            help="The time range for which to fetch data. (default: 'YEAR_1')"
        )
        parser.add_argument(
            "--max-workers", type=int, default=16,
            help="Maximum number of workers for fetching data. (default: 16)"
        )
        return parser.parse_args()

    def get_founder_data(self):
        founders = FounderFetcher.fetch_founders()
        FundCodeFetcher.set_founders(founders)
        return founders

    def run(self):
        if self.args.get_only_founders:
            for founder in self.founder_data:
                print(f"Code: {founder.get_code()}, Name: {founder.get_name()}")
            return

        if self.args.update:
            assets = Asset.from_csv(self.input_path)
            manager = FundDataManager(
                fund_price_range=self.args.range,
                max_workers=self.args.max_workers,
            )
            price_updater = PriceUpdater(assets, manager)
            updated_assets = price_updater.update_prices()

            raw_df = pd.DataFrame([obj.to_dict() for obj in updated_assets])
            raw_df = DataFrameUtils.postprocess_dataframe(raw_df)
            raw_df.to_csv(self.raw_output_path, index=False, encoding="utf-8")
            return

        if not self.args.input:
            manager = FundDataManager(
                fund_price_range=self.args.range,
                additional_founders=self.args.founders,
                max_workers=self.args.max_workers,
            )
            fund_codes_data = manager.get_fund_codes_data()
            assets = manager.fetch_fund_data(fund_codes_data)

            raw_df = pd.DataFrame([obj.to_dict() for obj in assets])
            raw_df = DataFrameUtils.postprocess_dataframe(raw_df)
            raw_df.to_csv(self.raw_output_path, index=False, encoding="utf-8")

        if not self.args.no_processed:
            if self.args.input:
                assets = Asset.from_csv(self.input_path)

            processor = DataProcessor(assets)
            processed_df = processor.process()
            processed_df = DataFrameUtils.postprocess_dataframe(processed_df)
            processed_df.to_csv(self.processed_output_path, index=False, encoding="utf-8")

    def _parse_input_path(self):
        if self.args.input:
            input_path = Path(self.args.input)
            if input_path.is_file():
                return input_path

    def _parse_output_directory_path(self):
        if self.args.output:
            output_path = Path(self.args.output)
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
            if output_path.exists() and output_path.is_dir():
                return output_path

    def _parse_raw_output_path(self, raw_csv_filename: str):
        if self.args.output and self.output_directory_path and self.raw_csv_filename:
            return self.output_directory_path / raw_csv_filename

    def _parse_processed_output_path(self, processed_csv_filename: str):
        if self.args.output and self.output_directory_path and self.processed_csv_filename:
            return self.output_directory_path / processed_csv_filename

    def _parse_args(self):
        if self.args.input and self.args.no_processed:
            raise ValueError("Cannot use --input and --no-processed together.")
        if self.args.input and self.args.get_only_founders:
            raise ValueError("Cannot use --input and --get-only-founders together.")
        if self.args.input and self.args.founders:
            raise ValueError("Cannot use --input and --founders together.")
        if self.args.update and not self.args.input:
            raise ValueError("Cannot use --update without an input file.")
        if self.args.update and self.args.get_only_founders:
            raise ValueError("Cannot use --update and --get-only-founders together.")
        if self.args.update and self.args.founders:
            raise ValueError("Cannot use --update and --founders together.")
        if self.args.get_only_founders and self.args.founders:
            raise ValueError("Cannot use --get-only-founders and --founders together.")

        if not self.raw_csv_filename:
            raise ValueError("Raw CSV filename must be specified.")
        if not isinstance(self.raw_csv_filename, str):
            raise ValueError("Raw CSV filename must be a string.")
        if not self.processed_csv_filename:
            raise ValueError("Processed CSV filename must be specified.")
        if not isinstance(self.processed_csv_filename, str):
            raise ValueError("Processed CSV filename must be a string.")

    def _check_validity(self):
        if self.args.input and not self.input_path:
            raise ValueError("Input file specified does not exist.")
        if self.args.output and not self.output_directory_path:
            raise ValueError("Output directory specified does not exist or is not a directory.")


if __name__ == '__main__':
    Main(
        raw_csv_filename="fund_data_raw.csv",
        processed_csv_filename="fund_data.csv",
    ).run()
