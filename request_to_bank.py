import aiohttp
import logging
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO)

Currencys = ["CHF", "GBP", "PLZ", "SEK", "XAU", "CAD"]

async def check_mess(message: str, from_term = False):
    result_data = ""
    result_data_term = []
    list_message = message.split(" ")
    if list_message[0] == 'exchange':
        date_ =  date.today()
        if len(list_message) > 1:
            
            list_currency = []
            for i in Currencys:
                if i in message:
                    list_currency.append(i)
                    
            if list_message[1].isdigit():
                quant_ = int(list_message[1])
                if quant_ > 10:
                    quant_ = 10
                for i in range(quant_):
                    current_date = (date_ - timedelta(days=i)).strftime('%d.%m.%Y')
                    result = await request_to_banc(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={current_date}')
                    if from_term:
                        result = await norm_data_term(result, list_currency)
                        result_data_term.append(result)
                    else:
                        result = await norm_data(result, list_currency)
                        result_data += result
            else:
                current_date = date_.strftime('%d.%m.%Y')
                result = await request_to_banc(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={current_date}')
                if from_term:
                    result = await norm_data_term(result, list_currency)
                    result_data_term.append(result)
                else:
                    result = await norm_data(result, list_currency)
                    result_data += result
        else:
            current_date = (date_).strftime('%d.%m.%Y')
            result = await request_to_banc(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={current_date}')
            if from_term:
                result = await norm_data_term(result)
                result_data_term.append(result)
            else:
                result = await norm_data(result)
                result_data += result                
    else:
        result_data = message
    if from_term:
        return result_data_term
    return result_data

async def request_to_banc(url):
    logging.info(f'query = {url}')
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                result = await response.json()
                return result
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))

async def norm_data(data_, list_currency = []):
    list_cur = ["USD", "EUR"] + list_currency
    str_data = data_['date']
    for i in data_['exchangeRate']:
        if i['currency'] in list_cur:
            str_data +=f'\n {i["currency"]}: sale = {i["saleRateNB"]}, purchase = {i["purchaseRateNB"]};'
    return f'{str_data}\n'

async def norm_data_term(data_, list_currency = []):
    list_cur = ["USD", "EUR"] + list_currency
    tup2_data = {}
    for i in data_['exchangeRate']:
        if i['currency'] in list_cur:
            tup2_data[i['currency']] = {'sale': i["saleRateNB"], 'purchase': i["purchaseRateNB"]}
    tup_data = {data_['date']: tup2_data}
    return tup_data
