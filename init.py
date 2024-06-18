from discord import Client, Intents, app_commands
from modules.logger import Logger

client = Client(intents = Intents.all())
tree = app_commands.CommandTree(client)
token = open('data/token.txt', 'r').read()
log = Logger()

GUILD_ID = 0
COLOR = 0x0
sync = False