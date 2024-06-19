from discord import Embed, Interaction, Member, SelectOption
from fun.funs import get_profile
from discord.ui import View, Select
from init import COLOR, tree

@tree.context_menu(
    name = "Speedmath profile"
)
async def speeedmathProfile(interaction: Interaction, member: Member):
    profile = await get_profile(member)
    if profile:
        options = [
            SelectOption(
                label = name,
                description = f'{len(profile[name])} game{'s' if len(profile[name]) > 1 else ''}'
            ) for name in profile.keys()
        ]
        if options != []:
            await interaction.response.send_message(
                embed = Embed(
                    title = "All games",
                    color = COLOR
                ).set_author(
                    name = member.display_name,
                    icon_url = member.display_avatar.url
                ),
                view = View(timeout = None).add_item(
                    Select(
                        placeholder = "Modes",
                        options = options,
                        custom_id = f"PROFILE#{interaction.user.id}#{member.id}"
                    )
                )
            )
            return
    
    await interaction.response.send_message(
        embed = Embed(
            title = "Nothing here",
            description = f"Looks like {member.display_name} has not played yet.",
            color = COLOR
        ),
        ephemeral = True
    )