import json
from copy import deepcopy

formats = {
    "italic": "*{text}*",
    "bold": "**{text}**",
    "underline": "__{text}__",
    "strikethrough": "~~{text}~~",
    "quote": "> {text}",
    "single_code": "`{text}`",
    "code": "```{text}```",
}
def format(text, *styles):
    message = text
    for style in styles:
        message = formats[style].format(text=message)
    return message

remove_chars = {
    "brackets": "[]{}",
    "parantheses": "()",
    "quotes": '""',
    "apostrophes": "''",
}

def remove_char(text, *remove_types):
    for remove_type in remove_types:
        for char in remove_chars[remove_type]:
            text = text.replace(char, "")
    return text


PROFILES_PATH = 'servers/servers.json'
def get_servers_data():
    with open(PROFILES_PATH, 'r') as f:
        data = json.load(f)
    return data

def set_servers_data(data):
    with open(PROFILES_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def guild_exists(guild_id: str):
    """checks if a guild exists, and if not, create it"""
    data = get_servers_data()
    if guild_id not in data:
        data[guild_id] = deepcopy(data['default'])
        set_servers_data(data)
        return False
    return True

def update_setting(guild_id: str, setting, new_value):
    data = get_servers_data()
    data[guild_id][setting] = new_value
    set_servers_data(data)



def filter_dunders(filter_list):
    return list(filter(lambda x: not x.startswith('__'), filter_list))

def responses():
    with open('responses.json', 'r') as f:
        return json.load(f)

# responses are put in list so they can be randomly accessed later when I feel like doing it >:(