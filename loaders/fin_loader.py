from pathlib import Path
import pandas as pd

from .base import BaseReportLoader


class FinReportLoader(BaseReportLoader):

    NAME = 'Fin Report Loader'

    def load_report(self, filepath: str | Path) -> pd.DataFrame:
        cols = ['transaction_datetime_provider', 'record_type_key',
                'amount', 'currency', 'geo_country', 'legal_entity']

        df = self.load_dataframe_from_file(filepath, usecols=cols)

        df = df[
            df['record_type_key'].isin({'SALE', 'REFUND', 'CHARGEBACK'}) &
            df['geo_country'].isin(COUNTRY_CODE_MAP)
        ]

        df['Country Code'] = df['geo_country'].map(COUNTRY_CODE_MAP)

        df['Date'] = pd.to_datetime(
            df['transaction_datetime_provider'],
            format='%m/%d/%Y %H:%M',
            errors='coerce'
        )

        df['Gross Amount'] = pd.to_numeric(
            df['amount'], errors='coerce').round(2)

        df = df.rename(columns={
            'legal_entity': 'Legal Entity',
            'currency': 'Currency'
        })

        df = df[['Date', 'Country Code', 'Gross Amount', 'Currency', 'Legal Entity']]

        return df


COUNTRY_CODE_MAP = {
    'GBR': 'UK',
    'POL': 'PL',
    'ROU': 'RO',
    'FRA': 'FR',
    'LTU': 'LT',
    'MLT': 'MT',
    'HUN': 'HU',
    'CZE': 'CZ',
    'AUT': 'AT',
    'ESP': 'ES',
    'EST': 'EE',
    'GRC': 'EL',
    'DEU': 'DE',
    'IRL': 'IE',
    'FIN': 'FI',
    'LVA': 'LV',
    'BEL': 'BE',
    'LUX': 'LU',
    'CYP': 'CY',
    'NLD': 'NL',
    'SVN': 'SI',
    'ITA': 'IT',
    'PRT': 'PT',
    'SVK': 'SK',
    'SWE': 'SE',
    'DNK': 'DK',
    'BGR': 'BG',
    'HRV': 'HR'
}
