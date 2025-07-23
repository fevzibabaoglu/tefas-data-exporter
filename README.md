# TEFAS Fund Data Exporter

A Python tool to fetch, process, and export fund data from TEFAS (Türkiye Elektronik Fon Alım Satım Platformu).


## Features

* Fetch fund data directly from TEFAS
* Optional support for one-year price data
* Process and clean raw data into a structured CSV


## Usage

```bash
python src/main.py [-h] [--input INPUT] [--output OUTPUT] [--include-price-chart] [--max-workers MAX_WORKERS]
```


### Options

| Argument                | Description                                                                  |
| ----------------------- | ---------------------------------------------------------------------------- |
| `--input`               | Optional path to a raw fund CSV. If provided, skips fetching real-time data. |
| `--output`              | Output directory to save the files. (default: 'output')                      |
| `--include-price-chart` | Include price chart data in raw data. (default: off)                         |
| `--max-workers`         | Maximum number of workers for fetching data. (default: 16)                   |


## Output

* `fund_data_raw.csv`: Raw fund data (only if fetched)
* `fund_data.csv`: Cleaned and processed fund data


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
