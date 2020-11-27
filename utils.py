import json
from copy import deepcopy
import discord
import random

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

PROFILES_PATH = 'servers.json'
def get_servers_data():
    with open(PROFILES_PATH, 'r') as f:
        data = json.load(f)
    return data

def set_servers_data(data):
    with open(PROFILES_PATH, 'w') as f:
        json.dump(data, f, indent=4)


def get_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_responses():
    with open('info/responses.json', 'r') as f:
        return json.load(f)

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

    
def embed_template(title=None, description=None):
    embed = discord.Embed(color=random.randint(0, 16777215))
    if title is not None:
        embed.title = title
    if description is not None:
        embed.description = description

    return embed