from init import *
from fun.loops import *
from asyncio import gather
import commands.commands

@client.event
async def on_ready():
    log.info('En ligne')
    if sync:
        cmds = await tree.sync()
        log.info(f'{len(cmds)} commandes slash synchronisées')
    
    tasks = []
    await gather(*tasks)