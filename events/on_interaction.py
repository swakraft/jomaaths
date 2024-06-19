import asyncio
from datetime import datetime, timedelta

from prettytable import PrettyTable
from classes.command import Command
from classes.engine import Engine
from fun.funs import add_game_to_profile, get_profile
from fun.views import game_stats_view
from init import COLOR, client, log
from discord import ButtonStyle, DMChannel, Embed, Interaction, Message, PermissionOverwrite, SelectOption, TextChannel, User
from discord.ui import View, Select, Button

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

                await interaction.response.edit_message(
                    embed = Embed(
                        title = "Game loaded",
                        description = "Press Start",
                        color = COLOR
                    ),
                    view = View(timeout = None).add_item(
                        Button(
                            label = "Start",
                            style = ButtonStyle.green,
                            custom_id = f"CONFIRMSTART#{interaction.user.id}"
                        )
                    )
                )
                def check_button(interaction2: Interaction):
                    return interaction2.user == interaction.user and interaction2.data['custom_id'].split('#')[0] == "CONFIRMSTART"

                interaction2: Interaction = await client.wait_for('interaction', check = check_button)
                stats:list[dict] = []
                first = True
                for calc in engine.calcs:
                    if first:
                        await interaction2.response.edit_message(
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
        
        case "STARTCHALLENGE":
            if id.split("#")[1] == str(interaction.user.id):
                target = client.get_user(int(id.split("#")[2]))
                difficulty_type = values[0]
                match difficulty_type:
                    case 'baby':
                        engine = Engine(
                            operations=['+', '*'],
                            lenght=2
                        )
                    
                    case 'easy':
                        engine = Engine(
                            range = [1, 10]
                        )
                
                c1 = await interaction.guild.create_text_channel(
                    name = interaction.user.display_name,
                    overwrites = {
                        interaction.user: PermissionOverwrite(read_messages = True, send_messages = True),
                        interaction.guild.default_role: PermissionOverwrite(read_messages = False)
                    }
                )
                c2 = await interaction.guild.create_text_channel(
                    name = target.display_name,
                    overwrites = {
                        target: PermissionOverwrite(read_messages = True, send_messages = True),
                        interaction.guild.default_role: PermissionOverwrite(read_messages = False)
                    }
                )

                await interaction.response.edit_message(
                    view = View(),
                    embed = Embed(
                        title = "Channels created",
                        description = f"Press Start in your channel\n{c1.mention} {c2.mention}",
                        color = COLOR
                    )
                )
                    
                async def handle_challenge(engine: Engine, user: User, channel: TextChannel | DMChannel):
                    await channel.send(
                        embed = Embed(
                            title = "Game loaded",
                            description = "Press Start",
                            color = COLOR
                        ),
                        view = View(timeout = None).add_item(
                            Button(
                                label = "Start",
                                style = ButtonStyle.green,
                                custom_id = f"CONFIRMCHALLENGESTART#{user.id}"
                            )
                        )
                    )
                    def check_button(interaction2: Interaction):
                        return interaction2.user == interaction.user and interaction2.data['custom_id'].split('#')[0] == "CONFIRMCHALLENGESTART"

                    interaction2: Interaction = await client.wait_for('interaction', check = check_button)
                    await interaction2.response.edit_message()
                    await interaction2.message.delete()
                    stats = []
                    for calc in engine.calcs:
                        await channel.send(content=str(calc), embed=None, view=None)

                        def check(message: Message):
                            return message.author.id == user.id and message.channel.id == channel.id
                        
                        start = datetime.now()
                        message: Message = await client.wait_for("message", check=check)
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
                            stat['success'] = True
                        else:
                            stat['success'] = False
                        
                        stats.append(stat)

                    return stats
                
                async def challenger_thread():
                    return await handle_challenge(engine, interaction.user, c1)

                async def challenged_thread():
                    return await handle_challenge(engine, target, c2)

                challenger_task = asyncio.create_task(challenger_thread())
                challenged_task = asyncio.create_task(challenged_thread())
                log.info('en cours')
                
                challenger_stats = await challenger_task
                challenged_stats = await challenged_task
                log.info(challenged_stats, challenger_stats)
                await c1.delete()
                await c2.delete()
                content_challenger, embed_challenger = game_stats_view(challenger_stats, difficulty_type, interaction.user)
                content_challenged, embed_challenged = game_stats_view(challenged_stats, difficulty_type, target)
                table = PrettyTable()
                for name, value in zip(challenger_stats, challenged_stats):
                    pass
                
                await interaction.edit_original_response(
                    content = f"## {interaction.user.display_name}:\n{content_challenger}## {target.display_name}:\n{content_challenged}",
                    embeds = [
                        embed_challenged,
                        embed_challenger
                    ]
                )