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

from data_manager import DataProcessor, FundDataManager
from data_struct import Asset
from tefas_requests import FounderFetcher, FundCodeFetcher
from utils import DataFrameUtils


def main():
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
    args = parser.parse_args()

    # Get founders
    founders = FounderFetcher.fetch_founders()
    FundCodeFetcher.set_founders(founders)

    if args.get_only_founders:
        for founder in founders:
            print(f"Code: {founder.get_code()}, Name: {founder.get_name()}")
        return

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.input:
        manager = FundDataManager(
            fund_price_range=args.range,
            additional_founders=args.founders,
            max_workers=args.max_workers,
        )

        assets = manager.fetch_all_fund_data()
        raw_df = pd.DataFrame([obj.to_dict() for obj in assets])
        raw_df = DataFrameUtils.postprocess_dataframe(raw_df)

        raw_csv_path = output_dir / "fund_data_raw.csv"
        raw_df.to_csv(raw_csv_path, index=False, encoding="utf-8")

    if not args.no_processed:
        if args.input:
            assets = Asset.from_csv(args.input)

        processor = DataProcessor(assets)
        processed_df = processor.process()
        processed_df = DataFrameUtils.postprocess_dataframe(processed_df)

        processed_csv_path = output_dir / "fund_data.csv"
        processed_df.to_csv(processed_csv_path, index=False, encoding="utf-8")


if __name__ == '__main__':
    main()
