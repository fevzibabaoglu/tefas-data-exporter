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

from data_manager import DataProcessor, FundDataManager, Utils
from data_struct import Asset


def main():
    parser = argparse.ArgumentParser(description="TEFAS Data Exporter")
    parser.add_argument(
        "--input", type=str, default=None,
        help="Optional path to a raw fund CSV. If provided, skips fetching real-time data."
    )
    parser.add_argument(
        "--output", type=str, default="output",
        help="Output directory to save the files. (default: 'output')"
    )
    parser.add_argument(
        "--include-price-chart", action="store_true",
        help="Include price chart data in raw data."
    )
    parser.add_argument(
        "--max-workers", type=int, default=16,
        help="Maximum number of workers for fetching data. (default: 16)"
    )
    parser.add_argument(
        "--no-processed", action="store_true",
        help="Do not include processed data in the output."
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.input:
        manager = FundDataManager(
            include_price_chart=args.include_price_chart,
            max_workers=args.max_workers
        )

        assets = manager.fetch_all_fund_data()
        raw_df = pd.DataFrame([obj.to_dict() for obj in assets])
        raw_df = Utils.postprocess_dataframe(raw_df)

        raw_csv_path = output_dir / "fund_data_raw.csv"
        raw_df.to_csv(raw_csv_path, index=False, encoding="utf-8")

    if not args.no_processed:
        if args.input:
            assets = Asset.from_csv(args.input)

        processor = DataProcessor(assets)
        processed_df = processor.process()
        processed_df = Utils.postprocess_dataframe(processed_df)

        processed_csv_path = output_dir / "fund_data.csv"
        processed_df.to_csv(processed_csv_path, index=False, encoding="utf-8")


if __name__ == '__main__':
    main()
