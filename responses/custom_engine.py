import re
from discord import ButtonStyle, Embed, Interaction, TextChannel
from init import COLOR, client, log
from classes.engine import Engine
from fun.views import define_operation, engine_editor_main
from discord.ui import Modal, TextInput, View, Button

from responses.default import invalid_parameter


async def main_custom_engine(interaction: Interaction, multiplayer: bool, channel1: TextChannel = None, channel2: TextChannel = None):
    engine = Engine() # init new blank engine
    embed, view = engine_editor_main(engine, interaction)
    await interaction.response.edit_message(embed = embed, view = view)
    def check_button(interaction2: Interaction):
        return interaction2.user == interaction.user and interaction2.channel == interaction.channel

    while True:
        interaction2: Interaction = await client.wait_for("interaction", check = check_button)
        match interaction2.data["custom_id"].split("#")[0]:
            case "STARTCUSTOM":
                if multiplayer:
                    await interaction.response.edit_message(
                        view = View(),
                        embed = Embed(
                            title = "Your custom game is ready!",
                            description = f"Press Start in your channel\n{channel1.mention} {channel2.mention}",
                            color = COLOR
                        )
                    )

                else:
                    await interaction2.response.edit_message(
                        embed = Embed(
                            title = "Your custom game is ready!",
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
                return engine
            
            case "DEFINENBCALCS":
                modal = Modal(title = "Define number of calculations")
                raw_nb_calc = TextInput(
                    label = "Number of calculations",
                    placeholder = "10",
                    default = engine.length
                )
                modal.add_item(raw_nb_calc)
                async def on_nb_calcs(interaction3: Interaction):
                    nb_calcs = raw_nb_calc.value.strip()
                    if nb_calcs.isnumeric():
                        engine.length = int(nb_calcs)
                        embed, view = engine_editor_main(engine, interaction3)
                        await interaction3.response.edit_message(embed = embed, view = view)

                    else:
                        await invalid_parameter(interaction3)
                
                modal.on_submit = on_nb_calcs
                await interaction2.response.send_modal(modal)
            
            case "DEFINEOP":
                match interaction2.data["custom_id"].split("#")[1]:
                    case "+":
                        embed, view, range = define_operation('+', engine, interaction2)
                        engine.range.add_range = range
                        current_operation = '+'
                        
                    case "-":
                        embed, view, range = define_operation('-', engine, interaction2)
                        engine.range.subtract_range = range
                        current_operation = '-'

                    case "*":
                        embed, view, range = define_operation('*', engine, interaction2)
                        engine.range.multiply_range = range
                        current_operation = '*'

                    case "/":
                        embed, view, range = define_operation('/', engine, interaction2)
                        engine.range.divide_range = range
                        current_operation = '/'

                await interaction2.response.edit_message(
                    embed = embed,
                    view = view
                )

                while True:
                    interaction3: Interaction = await client.wait_for('interaction', check = check_button)
                    match interaction3.data["custom_id"].split("#")[0]:
                        case "SETFREQU":
                            modal = Modal(title = f"Define {current_operation} operations")
                            raw_frequency = TextInput(
                                label = "Frequency [0, 1]",
                                placeholder = "0.25",
                                default = str(engine.operations_probs[current_operation])
                            )
                            modal.add_item(raw_frequency)

                            def checkfloat():
                                return re.match(r"^-?\d+(\.|,)?\d*$", raw_frequency.value.strip().replace(",", "."))
                            
                            match interaction3.data["custom_id"].split("#")[1]:
                                case "+":
                                    async def define_operation_frequency(interaction4: Interaction):
                                        valid = checkfloat()
                                        if valid:
                                            engine.operations_probs.add_prob = float(raw_frequency.value.strip().replace(",", "."))
                                            embed, view, l = define_operation('+', engine, interaction4)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )
                                        
                                        else:
                                            log.debug("not valid")
                                    
                                case "-":
                                    async def define_operation_frequency(interaction4: Interaction):
                                        valid = checkfloat()
                                        if valid:
                                            engine.operations_probs.subtract_prob = float(raw_frequency.value.strip().replace(",", "."))
                                            embed, view, l = define_operation('-', engine, interaction4)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )

                                case "*":
                                    async def define_operation_frequency(interaction4: Interaction):
                                        valid = checkfloat()
                                        if valid:
                                            engine.operations_probs.multiply_prob = float(raw_frequency.value.strip().replace(",", "."))
                                            embed, view, l = define_operation('*', engine, interaction4)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )

                                case "/":
                                    async def define_operation_frequency(interaction4: Interaction):
                                        valid = checkfloat()
                                        if valid:
                                            engine.operations_probs.divide_prob = float(raw_frequency.value.strip().replace(",", "."))
                                            embed, view, l = define_operation('/', engine, interaction4)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )
                                
                            modal.on_submit = define_operation_frequency
                            await interaction3.response.send_modal(modal)
                        
                        case "SETRANGE":
                            modal = Modal(title = f"Define {current_operation} range")
                            raw_range = TextInput(
                                label = "Range [minValue, maxValue]",
                                placeholder = "[1,10]",
                                default = str(engine.range[current_operation])
                            )
                            modal.add_item(raw_range)

                            def checkfloat():
                                try:
                                    str_values = raw_range.value.strip()[1:-1].split(",")
                                    new_range = [int(str_values[0].strip()), int(str_values[1].strip())]
                                    return new_range

                                except:
                                    raise ValueError("invalid format")
                            try:
                                match interaction3.data["custom_id"].split("#")[1]:
                                    case "+":
                                        async def define_operation_range(interaction4: Interaction):
                                            new_range = checkfloat()
                                            engine.range.add_range = new_range
                                            embed, view, range = define_operation('+', engine, interaction4)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )
                                        
                                    case "-":
                                        async def define_operation_range(interaction4: Interaction):
                                            new_range = checkfloat()
                                            engine.range.subtract_range = new_range
                                            embed, view, range = define_operation('-', engine, interaction4)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )

                                    case "*":
                                        async def define_operation_range(interaction4: Interaction):
                                            new_range = checkfloat()
                                            engine.range.multiply_range = new_range
                                            embed, view, range = define_operation('*', engine, interaction4)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )

                                    case "/":
                                        async def define_operation_range(interaction4: Interaction):
                                            new_range = checkfloat()
                                            engine.range.divide_range = new_range
                                            embed, view, range = define_operation('/', engine, interaction4)
                                            await interaction4.response.edit_message(
                                                embed = embed,
                                                view = view
                                            )

                            except ValueError:
                                await invalid_parameter(interaction3)

                                
                            modal.on_submit = define_operation_range
                            await interaction3.response.send_modal(modal)
                        
                        case "BACKTOMAINCUSTOM":
                            embed, view = engine_editor_main(engine, interaction)
                            await interaction3.response.edit_message(
                                embed = embed,
                                view = view
                            )
                            break
                    
                