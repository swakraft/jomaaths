from init import *
from fun.loops import *
from asyncio import gather
import commands.speedmath
import commands.context

@client.event
async def on_ready():
    log.info('En ligne')
    tree.add_command(commands.speedmath.speed_math_tree)
    if sync:
        cmds = await tree.sync()
        log.info(f'{len(cmds)} commandes slash synchronisées')
    
    tasks = []
    await gather(*tasks)