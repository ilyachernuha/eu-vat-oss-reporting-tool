from pathlib import Path
from typing import Dict
import sys
import pandas as pd

from config import config
from data import fetch_forex_rates, fetch_vat_rates
from loaders import loaders
from logger import logger

reporting_date = config['reporting_date']
input_folder = config['input_folder']
report_name = config['report_name']

reporting_date_obj = pd.to_datetime(reporting_date)

def main():

    # STEP 1: Load VAT rates from Taxes in Europe Database
    logger.info('Step 1/7: Getting VAT rates from Taxes in Europe Database...')
    try:
        vat_rates = fetch_vat_rates(reporting_date)
        logger.info(f'Fetched VAT rates: {vat_rates}')
    except Exception as e:
        logger.error('Unable to get VAT rates from Taxes in Europe Database. Exiting.')
        sys.exit(1)

    # STEP 2: Load FOREX rates from ECB Data Portal API
    logger.info('Step 2/7: Getting FOREX rates from ECB Data Portal API...')
    try:
        forex_rates = fetch_forex_rates(reporting_date)
        logger.info(f'Fetched FOREX rates: {forex_rates}')
    except Exception as e:
        logger.error('Unable to get FOREX rates from ECB Data Portal API. Exiting.')
        sys.exit(1)

    # STEP 3: Load reports
    logger.info('Step 3/7: Loading reports...')
    df = load_reports(input_folder)

    # STEP 4: Calculate VAT amounts
    logger.info('Step 4/7: Calculating VAT...')
    df = calculate_vat(df, vat_rates)

    # STEP 5: Convert Gross and VAT amounts to EUR
    logger.info('Step 5/7: Converting amounts to EUR...')
    df = convert_to_eur(df, forex_rates)

    # STEP 6: Prepare final report
    logger.info('Step 6/7: Generating the report...')
    df = generate_report(df)

    # STEP 7: Save generated report to Excel file
    logger.info('Step 7/7: Saving the report to Excel file...')
    try:
        write_report_to_excel(df, report_name)
    except Exception as e:
        logger.error('Unable to save the report. Try closing the file and rerunning the script. Exiting.')
        sys.exit(1)

    logger.info(f'Done! Report {report_name}.xlsx is ready!')


def load_reports(folder: str | Path) -> pd.DataFrame:

    dataframes = []

    for subfolder in Path(folder).iterdir():

        if not subfolder.is_dir():
            logger.warning(f'Skipping file: {subfolder.name}')
            continue

        report_type = subfolder.name

        loader = loaders.get(report_type)

        if not loader:
            logger.warning(f'No loader found for: {report_type}')
            continue

        logger.info(f'Loading folder: {subfolder.name}')
        dataframes.append(loader.load_folder(subfolder))

    res = pd.concat(dataframes, ignore_index=True)

    res = res[(res['Date'].dt.year == reporting_date_obj.year) & (
        res['Date'].dt.quarter == reporting_date_obj.quarter)]

    res['Month'] = res['Date'].dt.month

    return res


def calculate_vat(df: pd.DataFrame, vat_rates: Dict[str, float]) -> pd.DataFrame:
    df = df.copy()

    rates = df['Country Code'].map(vat_rates)

    missing = df.loc[rates.isna(), 'Country Code'].unique()
    if len(missing) > 0:
        logger.warning(f'Missing VAT rates for: {', '.join(missing)}')

    df['VAT'] = (df['Gross Amount'] * rates / (1 + rates)).round(2)

    return df


def convert_to_eur(df: pd.DataFrame, forex_rates: Dict[str, float]) -> pd.DataFrame:
    df = df.copy()

    rates = df['Currency'].map(forex_rates)

    missing = df.loc[rates.isna(), 'Currency'].unique()
    if len(missing) > 0:
        logger.warning(f'Missing FOREX rates for: {', '.join(missing)}')

    valid_rates = rates.replace(0, pd.NA)

    df['Gross_EUR'] = (df['Gross Amount'] / valid_rates).round(2)
    df['VAT_EUR'] = (df['VAT'] / valid_rates).round(2)

    return df


def generate_report(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(['Legal Entity', 'Country Code', 'Month'], as_index=False)
          [['Gross_EUR', 'VAT_EUR']].sum()
    )


def write_report_to_excel(df: pd.DataFrame, report_name: str) -> None:
    df.to_excel(f'{report_name}.xlsx', index=False)


if __name__ == '__main__':
    main()
