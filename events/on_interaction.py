from datetime import datetime, timedelta
from classes.command import Command
from classes.engine import Engine
from fun.funs import add_game_to_profile, get_profile
from fun.views import game_stats_view
from init import COLOR, client, log
from discord import Embed, Interaction, Message, SelectOption
from discord.ui import View, Select

@client.event
async def on_interaction(interaction: Interaction):
    if 'custom_id' in interaction.data:
        id = interaction.data['custom_id']
        if 'values' in interaction.data:
            values = interaction.data['values']
        
        else:
            values = None
        
        await interact(interaction, id, values)

async def interact(interaction: Interaction, id: str, values: list[str]):
    log.info(interaction.user.id, id)
    match id.split("#")[0]:
        case "START":
            if id.split("#")[1] == str(interaction.user.id):
                difficulty_type = values[0]
                match difficulty_type:
                    case 'baby':
                        engine = Engine(
                            operations=['+', '*'],
                            lenght=5
                        )
                    
                    case 'easy':
                        engine = Engine(
                            range = [1, 10]
                        )

                stats:list[dict] = []
                first = True
                for calc in engine.calcs:
                    if first:
                        await interaction.response.edit_message(
                            content = str(calc),
                            embed = None,
                            view = None
                        )
                        first = False
                    
                    else:
                        await interaction.channel.send(
                            content = str(calc)
                        )
                    
                    def check(message: Message):
                        return message.author.id == interaction.user.id and message.channel.id == interaction.channel.id
                    start = datetime.now()
                    message: Message = await client.wait_for("message", check = check)
                    end = datetime.now()
                    content = message.content.strip()
                    stat = {
                        "duration": (end - start).total_seconds(),
                        "calc": str(calc),
                        "user_answer": content,
                        "answer": calc.answer,
                        "date": int(datetime.now().timestamp())
                    }
                    
                    if int(content) == calc.answer:
                        #await message.add_reaction("✅")
                        stat['success'] = True
                    
                    else:
                        #await message.add_reaction("😐")
                        stat['success'] = False
                    
                    stats.append(stat)

                content, embed = game_stats_view(stats, difficulty_type, interaction.user)
                await interaction.channel.send(
                    content = content,
                    embed = embed
                )
                await add_game_to_profile(interaction.user, stats, difficulty_type.capitalize())
            
            else:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "This is not your game",
                        description = f"Start yout own game with {Command.speedmath_start}.",
                        color = COLOR
                    ),
                    ephemeral = True
                )

        case 'PROFILE':
            if str(interaction.user.id) == id.split("#")[1]:
                target = client.get_user(int(id.split("#")[2]))
                profile = await get_profile(target)
                games = profile[values[0]][::-1]
                txt = ""
                options = []
                for game in games:
                    s, f, = 0, 0
                    for calc in game:
                        if calc['success']: s += 1
                        else: f += 1

                    options.append(
                        SelectOption(
                            label = f"Game from {datetime.fromtimestamp(game[0]['date']).strftime("%d/%m/%y, %H:%M")}",
                            description = f"{s}/{s+f}",
                            value = game[0]["date"]
                        )
                    )
                    if len(options) >= 25:
                        break
                
                await interaction.response.edit_message(
                    embed = Embed(
                        title = f"{values[0].capitalize()}",
                        description = "Last games",
                        color = COLOR,
                    ).set_author(
                        name = target.display_name,
                        icon_url = target.display_avatar.url
                    ),
                    view = View(timeout = None).add_item(
                        Select(
                            placeholder = "Games",
                            options = options,
                            custom_id = f"PROFILETYPE#{interaction.user.id}#{target.id}#{values[0]}"
                        )
                    )
                )
        
        case "PROFILETYPE":
            if str(interaction.user.id) == id.split("#")[1]:
                target = client.get_user(int(id.split("#")[2]))
                profile = await get_profile(target)
                mode = id.split("#")[3]
                games = profile[mode]
                for game in games:
                    if game[0]['date'] == int(values[0]):
                        content, embed = game_stats_view(game, mode, target)
                        await interaction.response.edit_message(
                            content = content,
                            embed = embed
                        )