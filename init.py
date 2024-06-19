from discord import Client, Intents, app_commands
from modules.logger import Logger

intents = Intents.default()
intents.message_content = True
intents.members = True
client = Client(intents = intents)
tree = app_commands.CommandTree(client)
token = open('data/token.txt', 'r').read()
log = Logger()

GUILD_ID = 1130518317598265464
COLOR = 0xF01D26
sync = False