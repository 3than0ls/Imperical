import json

def make_smart_looking(text):
    return f'```py\n{text}```'

def make_clever_looking(text):
    return f'`{text}`'

def filter_dunders(filter_list):
    return list(filter(lambda x: not x.startswith('__'), filter_list))

def responses():
    with open('responses.json', 'r') as f:
        return json.load(f)

# responses are put in list so they can be randomly accessed later when I feel like doing it >:(