from typing import Dict
from zeep import Client

# This function might return wrong VAT rates in cases where
# several different VAT rates are marked as 'STANDARD' and 'DEFAULT'.
# Works fine for '2025-03-31' date.
def fetch_vat_rates(date: str) -> Dict[str, float]:

    wsdl = 'https://ec.europa.eu/taxation_customs/tedb/ws/VatRetrievalService.wsdl'

    client = Client(wsdl=wsdl)

    eu_countries_iso_codes = [
        'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI',
        'FR', 'UK', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL',
        'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'XI'
    ]

    request = {
        'memberStates': {'isoCode': eu_countries_iso_codes},
        'situationOn': date
    }

    response = client.service.retrieveVatRates(**request)

    rates = {}

    for entry in response['vatRateResults']:
        if entry['type'] == 'STANDARD' and entry['rate']['type'] == 'DEFAULT':
            if entry['memberState'] in rates:
                print(
                    f'[WARNING] Several VAT rates fetched for {entry['memberState']}')
            rates[entry['memberState']] = entry['rate']['value'] / 100

    return rates
