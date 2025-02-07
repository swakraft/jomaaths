from discord import Embed, Interaction
from init import client, COLOR

async def send(interaction: Interaction, title: str, description: str):
    await interaction.response.send_message(
        embed = Embed(
            title = title,
            description = description,
            color = COLOR
        ),
        ephemeral = True
    )

async def invalid_parameter(interaction: Interaction):
    await send(interaction, "Invalid parameter", "Please try again")