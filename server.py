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
    if message.split(" ")[0] == 'exchange':
        # logging.info(f'query2 = {message}')
        if message.split(" ")[1].isdigit():
            # logging.info(f'query3 = {message}')
            quant_ = message.split(" ")[1]
            logging.info(f'quant_ = {quant_}')
            date_ =  date.today()
            logging.info(f'date_ = {date_}')
            for i in range(quant_):
                logging.info(f'iteration = {i}')
                current_date = (date_ - timedelta(days=i)).strftime('%d.%m.%Y')
                logging.info(f'query6 = {current_date}')
                result = await request_to_banc(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={current_date}')
                logging.info(f'query8 = {result}')
                
    else:
        result = message
    return result

async def request_to_banc(message):
    logging.info(f'query7 = {message}')
    async with aiohttp.ClientSession() as session:            
        async with session.get(message) as response:
            result = await response.json()
            return result
    
async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())