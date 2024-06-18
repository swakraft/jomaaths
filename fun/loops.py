from init import client, log
from asyncio import sleep

async def loop():
    log.info("En ligne")
    while True:
        await sleep(7)