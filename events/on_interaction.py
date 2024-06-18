from init import client, log
from discord import Interaction

@client.event
async def on_interaction(interaction: Interaction):
    if 'custom_id' in interaction.data:
        id = interaction.data['custom_id']
        if 'values' in interaction.data:
            values = interaction.data['values']
        
        else:
            values = None
        
        await interact(interaction, id, values)

async def interact(interaction: Interaction, id: str, values: list):
    log.info(id)

    