import os
import aiofiles
from typing import Union
from json import loads, dumps
from discord import Interaction, Message, User, Member
from init import GUILD_ID, client

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
    guild = client.get_guild(GUILD_ID)
    if isinstance(user, User):
        member = guild.get_member(user)

    return guild.get_role(1252564160903118979) in member.roles # @lead monkey

async def get_setting(function: str, name: str):
    settings:dict = await read_file("settings.json")
    return settings[function][name]

async def add_game_to_profile(user: User | Member, stats: list[dict], game_type: str):
    ids = os.listdir("data/profiles")
    if f"{user.id}.json" in ids:
        profile:dict[str, list] = await read_file(f"profiles/{user.id}.json")
        if not game_type in profile:
            profile[game_type] = []
        
        profile[game_type].append(stats)
        await write_file(f'profiles/{user.id}.json', profile)
    
    else:
        await write_file(f'profiles/{user.id}.json', {game_type: [stats]})

async def get_profile(user: User | Member) -> dict[str, list[list[dict]]] | None:
    ids = os.listdir("data/profiles")
    if f"{user.id}.json" in ids:
        return await read_file(f"profiles/{user.id}.json")