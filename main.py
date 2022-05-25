from bot import WordyBot
from func import *

from os import getenv
TG_API_KEY = getenv("TG_API_KEY")
assert TG_API_KEY != "", "Please set bot API key with TG_API_KEY enviromental variable"

from json import load
with open("locale.json", encoding="utf-8") as f:
    _ = load(f)

mkdir("tmp")

WordyBot(TG_API_KEY, _).run()
