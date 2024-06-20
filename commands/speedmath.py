from init import COLOR
from discord import Embed, Interaction, Member, SelectOption
from discord.app_commands import Group
from discord.ui import View, Select

class CustomGroup(Group):
    pass

speed_math_tree = CustomGroup(name = "speedmath", description = "Minigame")

@speed_math_tree.command(
    name = "start",
    description = "Start new game"
)
async def startCommand(interaction: Interaction):
    await interaction.response.send_message(
        embed = Embed(
            title = "Game Settings",
            description = "Configure your game",
            color = COLOR
        ),
        view = View(timeout = None).add_item(
            Select(
                placeholder = "Game type",
                options = [
                    SelectOption(
                        label = "Baby",
                        description = "z=x∘y      ∘ ∈ {+,×}      x, y ∈ [1;10]      5 calcs",
                        value = "baby",
                        emoji = "😀"
                    ),
                    SelectOption(
                        label = "Easy",
                        description = "z=x∘y      ∘ ∈ {+,−,×,÷}      x, y ∈ [1;10]      12 calcs",
                        value = "easy",
                        emoji = "🙂"
                    )
                ],
                custom_id = f"START#{interaction.user.id}",
            )
        )
    )

@speed_math_tree.command(
    name = "challenge",
    description = "Challenge a member from the server"
)
async def challengeCommand(interaction: Interaction, member: Member):
    if not member.bot and not member.id == interaction.user.id:
        await interaction.response.send_message(
            embed = Embed(
                title = "Game Settings",
                description = f"Configure your game. Both {member.display_name} and you will have the same calculus.",
                color = COLOR
            ),
            view = View(timeout = None).add_item(
                Select(
                    placeholder = "Game type",
                    options = [
                        SelectOption(
                            label = "Baby",
                            description = "z=x∘y      ∘ ∈ {+,×}      x, y ∈ [1;10]      5 calcs",
                            value = "baby",
                            emoji = "😀"
                        ),
                        SelectOption(
                            label = "Easy",
                            description = "z=x∘y      ∘ ∈ {+,−,×,÷}      x, y ∈ [1;10]      12 calcs",
                            value = "easy",
                            emoji = "🙂"
                        )
                    ],
                    custom_id = f"STARTCHALLENGE#{interaction.user.id}#{member.id}",
                )
            )
        )
    
    else:
        await interaction.response.send_message(
            embed = Embed(
                title = "Nope",
                description = f"You can't challenge {member.display_name}",
                color = COLOR
            ),
            ephemeral = True
        )