from typing import Dict
import requests


def fetch_forex_rates(date: str) -> Dict[str, float]:

    url = f'https://data-api.ecb.europa.eu/service/data/EXR/D..EUR.SP00.A?startPeriod={date}&endPeriod={date}&format=jsondata&detail=dataonly'

    response = requests.get(url)

    response.raise_for_status()

    data = response.json()

    currencies = []
    for v in data['structure']['dimensions']['series'][1]['values']:
        currencies.append(v['id'])

    series = data['dataSets'][0]['series']

    rates = {}
    for key, value in series.items():
        currency_index = int(key.split(':')[1])
        currency = currencies[currency_index]
        rate = value['observations']['0'][0]
        rates[currency] = rate

    rates['EUR'] = 1

    return rates
