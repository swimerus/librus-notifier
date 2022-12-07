import json


def get_config_entry(entry):
    f = open('resources/config.json', 'r')
    config = json.load(f)
    return config[entry]