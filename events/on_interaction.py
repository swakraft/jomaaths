import asyncio
from datetime import datetime
from classes.command import Command
from classes.engine import Engine
from fun.funs import add_game_to_profile, get_profile
from fun.views import game_stats_view
from init import COLOR, client, log
from discord import ButtonStyle, Embed, Interaction, PermissionOverwrite, SelectOption, errors
from discord.ui import View, Select, Button
from responses.custom_engine import main_custom_engine

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
                if difficulty_type == "custom":
                    engine = await main_custom_engine(interaction, False)
                
                else:
                    engine = Engine.from_difficulty_id(difficulty_type)

                    await interaction.response.edit_message(
                        embed = Embed(
                            title = "Game ready !",
                            description = "Answer the calculations as quickly as possible! Press Start when ready!",
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

                log.info("Waiting for start")
                interaction2: Interaction = await client.wait_for('interaction', check = check_button)
                await interaction2.message.delete()
                stats = await engine.start(interaction.channel, interaction.user)
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
                try:
                    c1 = await interaction.guild.create_text_channel(
                        name = interaction.user.display_name,
                        overwrites = {
                            interaction.user: PermissionOverwrite(read_messages = True, send_messages = True),
                            interaction.guild.default_role: PermissionOverwrite(read_messages = False),
                            client.user: PermissionOverwrite(read_messages = True, send_messages = True),
                        }
                    )
                    c2 = await interaction.guild.create_text_channel(
                        name = target.display_name,
                        overwrites = {
                            target: PermissionOverwrite(read_messages = True, send_messages = True),
                            interaction.guild.default_role: PermissionOverwrite(read_messages = False),
                            client.user: PermissionOverwrite(read_messages = True, send_messages = True),
                        }
                    )
                
                except errors.Forbidden:
                    await interaction.response.send_message(
                        embed = Embed(
                            title = "Error",
                            description = "I don't have permissions to create channels",
                            color = COLOR
                        ),
                        ephemeral = True
                    )
                    return
                
                difficulty_type = values[0]
                if difficulty_type == "custom":
                    engine = await main_custom_engine(interaction, True, c1, c2)
                
                else:
                    engine = Engine.from_difficulty_id(difficulty_type)
                    await interaction.response.edit_message(
                        view = View(),
                        embed = Embed(
                            title = "Channels created",
                            description = f"Press Start in your channel\n{c1.mention} {c2.mention}",
                            color = COLOR
                        )
                    )
                
                async def challenger_thread():
                    await c1.send(
                        embed = Embed(
                            title = "Game loaded",
                            description = "Press Start",
                            color = COLOR
                        ),
                        view = View(timeout = None).add_item(
                            Button(
                                label = "Start",
                                style = ButtonStyle.green,
                                custom_id = f"CONFIRMCHALLENGESTART#{interaction.user.id}"
                            )
                        )
                    )
                    def check_button(interaction2: Interaction):
                        return interaction2.user == interaction.user and interaction2.data['custom_id'].split('#')[0] == "CONFIRMCHALLENGESTART"

                    interaction2: Interaction = await client.wait_for('interaction', check = check_button)
                    await interaction2.response.edit_message()
                    await interaction2.message.delete()
                    return await engine.start(c1, interaction.user)

                async def challenged_thread():
                    await c2.send(
                        embed = Embed(
                            title = "Game loaded",
                            description = "Press Start",
                            color = COLOR
                        ),
                        view = View(timeout = None).add_item(
                            Button(
                                label = "Start",
                                style = ButtonStyle.green,
                                custom_id = f"CONFIRMCHALLENGESTART#{target.id}"
                            )
                        )
                    )
                    def check_button(interaction2: Interaction):
                        return interaction2.user == target and interaction2.data['custom_id'].split('#')[0] == "CONFIRMCHALLENGESTART"

                    interaction2: Interaction = await client.wait_for('interaction', check = check_button)
                    await interaction2.response.edit_message()
                    await interaction2.message.delete()
                    return await engine.start(c2, target)

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
                challenger_points = 0
                challenged_points = 0
                for calc_challenger, calc_challenged in zip(challenger_stats, challenged_stats):
                    if calc_challenger['success'] and calc_challenged['success']:
                        if calc_challenger['duration'] < calc_challenged['duration']:
                            challenger_points += 1

                        else:
                            challenged_points += 1

                    elif calc_challenger['success']:
                        challenger_points += 1
                        
                    elif calc_challenged['success']:
                        challenged_points += 1
                
                await interaction.edit_original_response(
                    content = f"> Scores are calculated based on the speed of the fastest.\n## {interaction.user.display_name}:\nScore: {challenger_points}\n{content_challenger}## {target.display_name}:\nScore: {challenged_points}\n{content_challenged}\n\n\n",
                    embeds = [
                        embed_challenged,
                        embed_challenger
                    ]
                )