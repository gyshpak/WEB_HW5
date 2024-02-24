import asyncio
import aiohttp
import logging
import websockets
import names
from datetime import date, datetime, timedelta
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unsegister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnected')
    
    async def sent_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]
    
    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unsegister(ws)
    
    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            ansver_mess = await check_mess(message)
            await self.sent_to_clients(f'{ws.name}: {ansver_mess}')

async def check_mess(message: str) -> str:
    # logging.info(f'query1 = {message}')
    result_data = ""
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
                    result = await norm_data(result, list_currency)
                    result_data += result
            else:
                current_date = date_.strftime('%d.%m.%Y')
                result = await request_to_banc(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={current_date}')
                result = await norm_data(result, list_currency)
                result_data += result
        else:
            current_date = (date_).strftime('%d.%m.%Y')
            result = await request_to_banc(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={current_date}')
            result = await norm_data(result)
            result_data += result                
    else:
        result_data = message
    logging.info(f'result_data = {result_data}')
    return result_data

async def request_to_banc(message):
    logging.info(f'query7 = {message}')
    async with aiohttp.ClientSession() as session:            
        async with session.get(message) as response:
            result = await response.json()
            return result

async def norm_data(data_, list_currency = []):
    list_cur = ["USD", "EUR"] + list_currency
    str_data = data_['date']
    for i in data_['exchangeRate']:
        if i['currency'] in list_cur:
            str_data +=f'\n {i["currency"]}: sale = {i["saleRateNB"]}, purchase = {i["purchaseRateNB"]};'
    return f'{str_data}\n'


Currencys = ["CHF", "GBP", "PLZ", "SEK", "XAU", "CAD"]
    
async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())