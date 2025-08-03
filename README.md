# TEFAS Fund Data Exporter

A Python tool to fetch, process, and export fund data from TEFAS (Türkiye Elektronik Fon Alım Satım Platformu).


## Usage

```bash
python src/main.py [-h] [--input INPUT] [--output OUTPUT] [--no-processed] [--get-only-founders] [--founders FOUNDER_1 FOUNDER_2 ...] [--range RANGE] [--max-workers MAX_WORKERS]
```


### Options

| Argument                | Description                                                                  |
| ----------------------- | ---------------------------------------------------------------------------- |
| `--input`               | Optional path to a raw fund CSV. If provided, skips fetching real-time data. |
| `--output`              | Output directory to save the files. (default: 'output')                      |
| `--no-processed`        | Do not include processed data in the output.                                 |
| `--get-only-founders`   | Fetch only founder data and display.                                         |
| `--founders`            | List of founder codes for additional fetching.                               |
| `--range`               | The time range for which to fetch data. (default: 'YEAR_1') [options: 'WEEK_1', 'MONTH_1', 'MONTH_3', 'MONTH_6', 'YEAR_START', 'YEAR_1', 'YEAR_3', 'YEAR_5'] |
| `--max-workers`         | Maximum number of workers for fetching data. (default: 16)                   |


## Output

* `fund_data_raw.csv`: Raw fund data
* `fund_data.csv`: Additional cleaned and processed fund data


### Data

* `code`: Fund code
* `name`: Fund name
* `founder_code`: Code of the fund founder
* `founder_name`: Name of the fund founder
* `category`: Fund category
* `risk_score`: Fund risk score
* `market_share`: Fund market share
* `is_in_tefas`: Trading status on TEFAS
* `prices`: List of `date`-`value` dictionaries of fund price history
* `asset_distributions`: List of `name`-`amount` dictionaries of assets fund contains
* `date_range`: Date range of price data


## Requirements

```bash
pip install -r requirements.txt
```

**Note:** This project was developed and tested using **Python 3.13.5**. While it may work on other Python 3.x versions, compatibility is not guaranteed.


***

## License

This project is licensed under the terms of the **GNU Lesser General Public License v3.0**.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of **MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE**. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License and the GNU Lesser General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

The full text of the licenses can be found in the root of this project:

*   **[COPYING](./COPYING)** (The GNU General Public License)
*   **[COPYING.LESSER](./COPYING.LESSER)** (The GNU Lesser General Public License)
