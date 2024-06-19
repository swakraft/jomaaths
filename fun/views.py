from discord import Embed, User
from prettytable import PrettyTable

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
    description = f"# {s}/{s+f}\n### Times\nAverage: {average} s      Fastest: {min_time} s      Slowest: {max_time} s"
    embed = Embed(
        title = "Results",
        description = description,
        color = COLOR
    ).set_footer(text = difficulty_type).set_author(name = user.display_name, icon_url = user.display_avatar.url)
    return txt, embed