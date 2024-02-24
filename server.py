import asyncio
import logging
import names
import platform
import websockets
from request_to_bank import *
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

    
async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())