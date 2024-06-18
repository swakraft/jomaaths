import aiofiles
from typing import Union
from json import loads, dumps
from discord import Message, User, Member
from init import client

async def read_file(name: str) -> Union[str, list, dict]:
    async with aiofiles.open(f'data/{name}', 'r') as async_readable_file:
        content = await async_readable_file.read()
        await async_readable_file.close()
        if name.endswith('.json'):
            return loads(content)
        
        return content

async def write_file(name: str, data: Union[str, list, dict]) -> None:
    async with aiofiles.open(f'data/{name}', 'w') as async_writable_file:
        if isinstance(data, (dict, list)):
            await async_writable_file.write(dumps(data, indent = 4))
        
        else:
            await async_writable_file.write(data)
        
        await async_writable_file.close()
    
async def fetch(channel_id: int, message_id: int) -> Message:
    return await client.get_channel(channel_id).fetch_message(message_id)

def is_manager(user: Union[User, Member]) -> bool:
    return not set([role.id for role in user.roles]).isdisjoint([])

async def get_setting(function: str, name: str):
    settings:dict = await read_file("settings.json")
    return settings[function][name]

