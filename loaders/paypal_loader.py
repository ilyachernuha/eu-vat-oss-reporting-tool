from pathlib import Path
import pandas as pd

from logger import logger

from .base import BaseReportLoader


class PaypalActivityReportLoader(BaseReportLoader):

    NAME = 'PayPal Activity Report Loader'

    MAPPING_PATH = Path(
        'input/mappings/Transactions mapping - LOOK AT ME FIRST.xlsx')

    def __init__(self) -> None:
        try:
            self.allowed_types = self.load_mapping(self.MAPPING_PATH)
        except FileNotFoundError:
            logger.warning(f'Mapping file for PayPal loader not found: {self.MAPPING_PATH.name}')
            self.allowed_types = set()

    def load_report(self, filepath: str | Path) -> pd.DataFrame:

        filepath = Path(filepath)

        if not self.allowed_types:
            raise ValueError('Mapping is empty')

        cols = ['Date', 'Type', 'Gross', 'Currency',
                'Transaction Buyer Country Code']

        df = self.load_dataframe_from_file(filepath, usecols=cols)

        df = df[
            df['Type'].isin(self.allowed_types) &
            df['Transaction Buyer Country Code'].isin(COUNTRY_CODE_MAP)
        ]

        df['Country Code'] = df['Transaction Buyer Country Code'].map(COUNTRY_CODE_MAP)

        df['Date'] = pd.to_datetime(
            df['Date'],
            format='%d/%m/%Y',
            errors='coerce'
        )

        df['Gross'] = df['Gross'].astype(str)
        df['Gross Amount'] = (
            df['Gross']
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
            .round(2)
        )

        df['Legal Entity'] = self.extract_entity_name(filepath.name)

        df = df[['Date', 'Country Code', 'Gross Amount', 'Currency', 'Legal Entity']]

        return df
    
    def extract_entity_name(self, filename: str) -> str:
        try:
            return filename.split(' - ')[0].split('. ', 1)[-1]
        except IndexError:
            return 'Unknown'

    def load_mapping(self, filepath: str | Path) -> set:
        df = self.load_dataframe_from_file(filepath, usecols=['Paypal desc', 'Mapping'])
        df.dropna(subset=['Paypal desc', 'Mapping'], inplace=True)
        allowed_labels = {'Sales', 'Refund', 'Chargeback'}
        allowed_types = set(
            df[df['Mapping'].isin(allowed_labels)]['Paypal desc']
        )
        return allowed_types

COUNTRY_CODE_MAP = {
    'AT': 'AT',
    'BE': 'BE',
    'BG': 'BG',
    'HR': 'HR',
    'CY': 'CY',
    'CZ': 'CZ',
    'DK': 'DK',
    'EE': 'EE',
    'FI': 'FI',
    'FR': 'FR',
    'DE': 'DE',
    'GR': 'EL',
    'HU': 'HU',
    'IE': 'IE',
    'IT': 'IT',
    'LV': 'LV',
    'LT': 'LT',
    'LU': 'LU',
    'MT': 'MT',
    'NL': 'NL',
    'PL': 'PL',
    'PT': 'PT',
    'RO': 'RO',
    'SK': 'SK',
    'SI': 'SI',
    'ES': 'ES',
    'SE': 'SE',
    'GB': 'UK'
}
