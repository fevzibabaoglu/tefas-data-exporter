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
import pandas as pd


class DataFrameUtils:
    @staticmethod
    def postprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Convert numeric columns to Int64 if they are all integers
        # This is useful for handling NaN values in integer columns
        df = df.apply(
            lambda col: col.astype('Int64')
            if pd.api.types.is_float_dtype(col) and \
                col.dropna().apply(float.is_integer).all()
            else col
        )

        # Convert string columns that look like lists or dictionaries to actual lists or dictionaries
        # This is useful for columns that contain string representations of lists or dictionaries
        df = df.apply(
            lambda col: col.apply(DataFrameUtils._parse_to_literal)
            if pd.api.types.is_string_dtype(col)
            else col
        )

        return df

    @staticmethod
    def _parse_to_literal(x):
        try:
            return ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return x
