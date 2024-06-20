import asyncio
from datetime import datetime, timedelta
import re
from discord.ui import Modal, TextInput
from classes.command import Command
from classes.engine import Engine, RangeSettings
from fun.funs import add_game_to_profile, get_profile
from fun.views import define_operation, engine_editor_main, game_stats_view
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
                            length=5
                        )
                    
                    case 'easy':
                        engine = Engine()
                    
                    case 'normal':
                        engine = Engine(
                            length = 15,
                            range = RangeSettings(
                                add_range = [1, 100],
                                subtract_range = [1, 100],
                                divide_range = [1, 100],
                                multiply_range = [1, 10]
                            )
                        )
                    
                    case 'custom':
                        length = None
                        engine = Engine()
                        embed, view = engine_editor_main(engine, interaction)
                        await interaction.response.send_message(
                            embed = embed,
                            view = view
                        )
                        
                        async def editor_button_press_check(interaction: Interaction):
                            id = interaction.data['custom_id'].split('#')[0]
                            log.info(interaction.user.id == int(id.split("#")[1]), id.split("#")[0] in ["DEFINNBCALCS", "DEFINE+OP", "DEFINE-OP", "DEFINE/OP", "DEFINE/OP"])
                            return interaction.user.id == int(id.split("#")[1]) and id.split("#")[0] in ["DEFINNBCALCS", "DEFINE+OP", "DEFINE-OP", "DEFINE/OP", "DEFINE/OP"]
                    
                        async def define_operation_press_check(interaction: Interaction):
                            id = interaction.data['custom_id'].split('#')[0]
                            return interaction.user.id == int(id.split("#")[1]) and re.match(r"^SET[\+\-\/\*](FREQ|RANGE)$", id.split("#")[0])
                        
                        while True:
                            log.info('waiting for define, start button')
                            interaction2: Interaction = await client.wait_for("interaction", check = editor_button_press_check)
                            log.info("interaction2")
                            i2_id = interaction2.data["custom_id"]
                            if i2_id.split("#")[0] == "DEFINENBCALCS":
                                modal = Modal(
                                    title = "Number of calcs"
                                )
                                raw_length = TextInput(
                                    label = "Number of calculus",
                                    placeholder = 10,
                                    default = length
                                )
                                modal.add_item(raw_length)
                                async def got_length(interaction3: Interaction):
                                    length = int(raw_length.value)
                                    engine.length = length
                                    embed, view = engine_editor_main(engine, interaction)
                                    if length > 0:
                                        await interaction3.response.edit_message(
                                            embed = embed,
                                            view = view
                                        )
                                    
                                    else:
                                        await interaction.response.edit_message(
                                            embed = Embed(
                                                title = "Error",
                                                description = "Length cannot must be superior to 0",
                                                color = COLOR
                                            )
                                        )
                                
                                modal.on_submit = got_length
                                await interaction2.response.send_modal(modal)
                            
                            elif re.match(r"^DEFINE", i2_id):
                                embed, view, range = define_operation(interaction2.data['custom_id'][6], engine, interaction)
                                await interaction2.response.edit_message(
                                    embed = embed,
                                    view = view
                                )
                                while True:
                                    log.info('waiting for range, frequency, back button')
                                    interaction3: Interaction = await client.wait_for('interaction', check = define_operation_press_check)
                                    i3_id = interaction3.data["custom_id"]
                                    if re.match(r"^SET[\+\-\/\*]RANGE$", i3_id.split("#")[0]):
                                        operation = i3_id[3]
                                        modal = Modal(
                                            title = f"Customize range '{operation}'"
                                        )
                                        raw_min_range = TextInput(
                                            label = "Min number",
                                            placeholder = 1,
                                            default = range[0]
                                        )
                                        raw_max_range = TextInput(
                                            label = "Max number",
                                            placeholder = 1,
                                            default = range[1]
                                        )
                                        modal.add_item(raw_min_range).add_item(raw_max_range)
                                        async def got_range(interaction4: Interaction):
                                            min_range = int(raw_min_range.value)
                                            max_range = int(raw_max_range.value)
                                            match operation:
                                                case '+':
                                                    engine.range.add_range = [min_range, max_range]
                                                
                                                case '-':
                                                    engine.range.subtract_range = [min_range, max_range]

                                                case '/':
                                                    engine.range.divide_range = [min_range, max_range]

                                                case '*':
                                                    engine.range.multiply_range = [min_range, max_range]
                                            
                                            embed, view, range = define_operation(operation, engine, interaction)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )
                                        
                                        modal.on_submit = got_range
                                        await interaction3.response.send_modal(modal)
                                    
                                    elif re.match(r"^SET[\+\-\/\*]FREQU$", i3_id.split("#")[0]):
                                        operation = i3_id[3]
                                        modal = Modal(
                                            title = f"Frequency of {operation}"
                                        )
                                        match operation:
                                            case '+':
                                               frequency = engine.operations_probs[0]
                                            
                                            case '-':
                                                frequency = engine.operations_probs[1]

                                            case '/':
                                                frequency = engine.operations_probs[2]

                                            case '*':
                                                frequency = engine.operations_probs[3]

                                        raw_frequency = TextInput(
                                            label = "Frequency [0~1]",
                                            placeholder = "0.25",
                                            default = str(frequency)
                                        )
                                        modal.add_item(raw_frequency)
                                        async def got_frequency(interaction4: Interaction):
                                            frequency = float(raw_frequency.value)
                                            match operation:
                                                case '+':
                                                    engine.operations_probs[0] = frequency
                                                
                                                case '-':
                                                    engine.operations_probs[1] = frequency

                                                case '/':
                                                    engine.operations_probs[2] = frequency

                                                case '*':
                                                    engine.operations_probs[3] = frequency
                                            
                                            embed, view, range = define_operation(operation, engine, interaction)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )
                                        
                                        modal.on_submit = got_frequency
                                        await interaction3.response.send_modal(modal)
                                    
                                    elif i3_id.split("#")[0] == "BACKTOMAINCUSTOM":
                                        embed, view = engine_editor_main(engine, interaction)
                                        await interaction3.response.send_message(
                                            embed = embed,
                                            view = view
                                        )
                                        break
                            
                            elif i2_id.split('#')[0] == "STARTCUSTOM":
                                interaction = interaction2
                                break

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
                    log.debug(type(content), content)
                    stat = {
                        "duration": (end - start).total_seconds(),
                        "calc": str(calc),
                        "user_answer": content,
                        "answer": calc.answer,
                        "date": int(datetime.now().timestamp())
                    }
                    try: 
                        content = int(content)
                    
                    except:
                        message.reply(content = "Please only send numbers")
                    
                    if content == calc.answer:
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
                            length=5
                        )
                    
                    case 'easy':
                        engine = Engine(
                            range = [1, 10],
                            length = 12
                        )
                    
                    case 'normal':
                        engine = Engine(
                            length = 15,
                            range = RangeSettings(
                                add_range = [1, 100],
                                subtract_range = [1, 100],
                                divide_range = [1, 100],
                                multiply_range = [1, 10]
                            )
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
                    return await handle_challenge(engine, interaction.user, c1)

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
                    content = f"## {interaction.user.display_name}:\nScore {challenger_points}\n{content_challenger}## {target.display_name}:\nScore {challenged_points}\n{content_challenged}\n\n> scrores are calculated based on the speed of the fastest.\n\n",
                    embeds = [
                        embed_challenged,
                        embed_challenger
                    ]
                )