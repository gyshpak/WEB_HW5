import asyncio
import logging
import platform
import sys
from request_to_bank import *

logging.basicConfig(level=logging.INFO)

async def main(args):
    resault = await check_mess(args, True)
    logging.info(resault)


if __name__ == "__main__":
    inp_ = " ".join(i for i in sys.argv[1:])
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(inp_))