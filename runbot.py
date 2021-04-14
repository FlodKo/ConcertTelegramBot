import sys
import json

with open('config.json') as json_file:
    config = json.load(json_file)
    config = config["api"]

from bot import BOT
BOT = BOT(config["bot_api_key"])
BOT.Main()