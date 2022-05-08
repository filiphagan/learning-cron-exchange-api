#!/usr/bin/env python

"""
Main.py: sends request to the forex market API, processes and saves the data into
csv files. stores backup
"""

__author__ = "Filip Hagan"

import os
import sys
import csv
import time
import logging
import requests

from typing import List
from datetime import datetime
from argparse import ArgumentParser

# Logging settings. Logs are being saved in ./api.log
logging.basicConfig(filename="api.log")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.info(f"Run started at {time.asctime()}")

parser = ArgumentParser()
parser.add_argument("--cache", default=7, type=int, help="Max amount of files saved in the cache directory")
args = parser.parse_args()

api_url = "http://api.exchangeratesapi.io/v1/latest"
access_key = "43673974d95862ae26a256e8ec439c68"
base = "EUR"
symbols = ["USD", "GBP", "SEK", "PLN", "RUB"]
output_dir = "/code/outputs"
output_lim = args.cache

params = {
    "access_key": access_key,
    "base": base,
    "symbols": ",".join(symbols)
}


def get_data(get_params: dict, url: str = "http://api.exchangeratesapi.io/v1/latest") -> dict:
    """Sends GET request to given API. Returns dictionary with metadata and currency:rates key pairs

    Parameters
    ----------
    get_params : dict
        Expected parameters acc. to https://exchangeratesapi.io/documentation/
    url : str, default "http://api.exchangeratesapi.io/v1/latest"
        Exchange Rates API URL

    Returns
    ----------
    result : dict
        Result example:
            {
            'success': True,
            'timestamp': 1649102286,
            'base': 'EUR',
            'date': '2022-04-04',
            'rates': {
                'USD': 1.097033,
                'GBP': 0.836548,
                'SEK': 10.346008,
                'PLN': 4.622403,
                'RUB': 91.602919
                }
            }
    """
    try:
        r = requests.get(url, params=get_params)
    except requests.exceptions.RequestException as e:
        logger.error(f"{time.asctime()}: Request did not succeed. Error: {e}")
        return {}

    if r.status_code != 200:
        logger.error(f"{time.asctime()}: Expected status code 200. Status code: {r.status_code}")
        return {}

    result = r.json()
    if not result["success"]:
        logger.error(f"{time.asctime()}: Request did not succeed.")
        return {}

    return result


def save_csv(output_directory: str, base_currency: str, currencies: List[str], timestamp: float, rates: dict) -> None:
    """Saves currency rates into formatted CSV file, returns None.
    Columns in the file represent exchange rates BASE/CURRENCY e.g. EUR/USD, EUR/PLN, EUR/GBP...

    Parameters
    ----------
    output_directory : str
        Output directory cache for CSV files
    base_currency : str
        Base currency for exchange rates
    currencies : list[str]
        List of currencies for exchange rates
    timestamp : float
        Timestamp from the API response
    rates : dict[str:float]
        Exchange rates from the API response
    """

    pretty_timestamp = datetime.utcfromtimestamp(timestamp).strftime("%Y%m%d%H%M%S")
    output_filename = f"{pretty_timestamp}_{base_currency}.csv"
    output_full_path = os.path.join(output_directory, output_filename)

    # Sometimes the API does not update the values after the last call (too frequent calls)
    # API timestamp remains unchanged
    if os.path.exists(output_full_path):
        logger.info(f"File {output_filename} already exist. Consider changing call frequency.")
    else:
        with open(output_full_path, "w") as f:
            try:
                writer = csv.DictWriter(f, fieldnames=currencies)
                writer.writeheader()
                writer.writerow(rates)
            except Exception as e:  # TODO: proper error handling
                logger.error(f"{time.asctime()}: Unable to save the file. Error: {e}")
                raise e


def clear_cache(directory: str, limit: int) -> None:
    """Deletes the oldest files in given directory if specific limit is exceeded
    Files are sorted by name. Expecting proper timestamp prefix.

    Parameters
    ----------
    directory : str
        path to data cache where csv files are stored

    limit : int
        max amount of files in the directory
    """

    if os.path.isdir(directory):
        files = os.listdir(directory)
        # TODO: check if file names match certain regex pattern
        if len(files) > limit:
            files_to_remove = sorted(files)[:len(files) - limit]
            try:
                for file in files_to_remove:
                    os.remove(os.path.join(directory, file))
            except OSError as e:
                logger.error(f"{time.asctime()}: Unable to clean the cache. Error: {e}")
                raise e
            logger.info(f"Cache cleaning done.")
        files = os.listdir(directory)
        logger.info(f"Cache size: {len(files)}")
        return
    else:
        e = f"{time.asctime()}: Directory {directory} does not exist."
        logger.error(e)
        raise Exception(e)


if __name__ == "__main__":

    # Call API and save the response into dict
    response = get_data(params, api_url)
    if not response:
        error = f"{time.asctime()}: Empty response."
        logger.error(error)
        raise ValueError(error)

    # Save the output file in cache directory
    save_csv(output_dir, base, symbols, response["timestamp"], response["rates"])

    # End with cache cleaning
    clear_cache(output_dir, output_lim)
    logger.info(f"Run ended at {time.asctime()}")
