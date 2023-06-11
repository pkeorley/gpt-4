from client import DiscordBotClient
from config import Config

bot = DiscordBotClient()
bot.load_extension("cogs.events")

Config.PATH = r"venv\.env"
bot.run(Config.config()["DISCORD_BOT_TOKEN"])
