import disnake
from disnake import Embed
from disnake.ext import commands

from client import DiscordBotClient
from config import Config


class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBotClient = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        prefix = await self.bot.command_prefix(message)

        if message.content.startswith(tuple(prefix)):
            return

        elif self.bot.user.mention in message.content:
            embed = Embed(
                description="A discord bot that provides access to many *neural models* right on your server, for more "
                            "information enter /help",
                color=Config.config()["COLOR"]
            ).set_author(
                name=self.bot.user,
                icon_url=self.bot.user.display_avatar.url
            )
            await message.reply(embed=embed)


def setup(bot):
    bot.add_cog(Handler(bot))
