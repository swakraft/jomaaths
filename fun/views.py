from typing import Literal
from discord import ButtonStyle, Embed, Interaction, User
from prettytable import PrettyTable
from discord.ui import View, Button
from init import log

from classes.engine import Engine
from init import COLOR

def game_stats_view(stats: list[dict], difficulty_type: str, user: User):
    table = PrettyTable()
    table.field_names = ["Time", "Calc", "You", "Ans", ""]
    for entry in stats:
        time = f"{entry['duration']:.2f}"
        calc = entry["calc"]
        user_answer = entry["user_answer"]
        answer = entry["answer"]
        if int(answer) == answer:
            answer = int(answer)
        success = "✅" if entry["success"] else "❌"
        
        table.add_row([time, calc, user_answer, answer, success])

    table.border = False
    table.header = True
    table.hrules = False
    table.align = "l"
    txt = ""
    for l in table.get_string().split("\n"):
        txt += f"`{l}`\n"

    f, s = 0, 0
    times: list[int] = []
    min_time = None
    max_time = None
    for stat in stats:
        if stat["success"]:
            s += 1
        
        else:
            f += 1
        
        time = round(stat['duration'], 1)
        times.append(time)
        if not max_time:
            max_time = time
        
        elif max_time < time:
            max_time = time
        
        if not min_time:
            min_time = time
        
        elif min_time > time:
            min_time = time
    
    average = int(sum(times)/len(stats))
    description = f"# {s}/{s+f}\n### Times\nAverage: {average}s      Fastest: {min_time}s      Slowest: {max_time}s"
    embed = Embed(
        title = "Results",
        description = description,
        color = COLOR
    ).set_footer(text = difficulty_type).set_author(name = user.display_name, icon_url = user.display_avatar.url)
    return txt, embed

def engine_editor_main(engine: Engine, interaction: Interaction):
    log.debug(engine)
    embed = Embed(
        title = "Math engine editor",
        description = f"Customize your math editor\n\n**Length:** {engine.length}\n",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Define number of calcs",
            custom_id = f"DEFINENBCALCS#{interaction.user.id}",
            style = ButtonStyle.blurple
        )
    ).add_item(
        Button(
            label = "Define + operations",
            custom_id = f"DEFINE+OP#{interaction.user.id}",
            style = ButtonStyle.blurple
        )
    ).add_item(
        Button(
            label = "Define - operations",
            custom_id = f"DEFINE-OP#{interaction.user.id}",
            style = ButtonStyle.blurple
        )
    ).add_item(
        Button(
            label = "Define * operations",
            custom_id = f"DEFINE*OP#{interaction.user.id}",
            style = ButtonStyle.blurple
        )
    ).add_item(
        Button(
            label = "Define / operations",
            custom_id = f"DEFINE/OP#{interaction.user.id}",
            style = ButtonStyle.blurple
        )
    ).add_item(
        Button(
            label = "Start Game",
            style = ButtonStyle.green,
            custom_id = f"STARTCUSTOM#{interaction.user.id}"
        )
    )
    return embed, view

def define_operation(operation: Literal['+', '-', '/', '*'], engine: Engine, interaction: Interaction):
    log.debug(engine)
    match operation:
        case '+':
            range = engine.range.add_range
        
        case '-':
            range = engine.range.subtract_range
        
        case '/':
            range = engine.range.divide_range
        
        case '*':
            range = engine.range.multiply_range

    embed = Embed(
        title = f"Customize operation '{operation}'",
        description = f"**Frequency:** {engine.operations_probs[0 if operation == '+' else 1 if operation == '-' else 2 if operation == '/' else '*']}\n**Range:** [{range[0]};{range[1]}]",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Define frequency",
            style = ButtonStyle.blurple,
            custom_id = f"SET{operation}FREQU#{interaction.user.id}"
        )
    ).add_item(
        Button(
            label = "Define range",
            custom_id = f"SET{operation}RANGE#{interaction.user.id}",
            style = ButtonStyle.blurple
        )
    ).add_item(
        Button(
            label = "Back",
            custom_id = f"BACKTOMAINCUSTOM#{interaction.user.id}"
        )
    )
    return embed, view, range