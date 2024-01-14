import asyncio
import aiohttp
import logging
import sys
from datetime import datetime, timedelta
from time import time


URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="
CURRENCY = ('EUR', 'USD')


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                logging.error(f"Error status: {response.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as error:
            logging.error(f"Connection error: {str(error)}")
            return None


def urls_for_days(days='1') -> list:
    current_date = datetime.now().date()
    dates = [current_date - timedelta(i) for i in range(int(days))]
    urls = [URL + date.strftime('%d.%m.%Y') for date in dates]
    return urls


async def get_exchange(currency_code='USD', days='1'):
    exchange_result = []
    urls = urls_for_days(days)
    tasks = [request(url) for url in urls]
    results = await asyncio.gather(*tasks)
    if results:
        for result in results:
            rates = result.get("exchangeRate")
            exchange, = list(filter(lambda element: element['currency'] == currency_code, rates))
            exchange_result.append(f"{currency_code}: buy: {exchange['purchaseRateNB']}, sale: {exchange['saleRateNB']}. Date: {result.get('date')}")
        
    if not exchange_result:
        return 'Data was not found'
    else:
        return exchange_result


async def get_currency_rates(currency_tuple=CURRENCY, days='1'):
    results = []
    for currency in currency_tuple:
        try:
            result = await get_exchange(currency, days)
            results.append(result)
        except KeyError:
            results.append(f"Failed to get currency rates for {currency}")
    return results


async def main():
    user_input = sys.argv
    days = user_input[1]
    if not days:
        return "Please, enter amount of days"
    if int(days) > 10:
        return 'You cannot get currency rates for more then 10 days'
    currency_tuple = CURRENCY
    if len(user_input) > 2:
        currency_tuple = tuple(list(CURRENCY) + [currency for currency in user_input[2:] if currency not in CURRENCY])

    try:
        result = await get_currency_rates(currency_tuple, days)
    except ValueError:
        return "Wrong Value"
    
    return result


if __name__ == '__main__':
    start = time()
    print(asyncio.run(main()))
    print(f"Total time: {time() - start}")