import os

import disnake
from disnake.ext import commands

from client import DiscordBotClient


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBotClient = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for filename in os.listdir("cogs"):
            if filename.endswith(".py") and not filename.startswith("event"):
                try:
                    self.bot.load_extension(f"cogs.{filename[:-3]}")
                    print(f"✅ cogs.{filename[:-3]} is loaded!")
                except commands.errors.ExtensionNotLoaded as error:
                    print(f"⛔ {error}")

        await self.bot.change_presence(activity=disnake.Game(
            name=f"{len(self.bot.guilds):,} guilds | {len(self.bot.users):,} members"
        ))
        print(f"🙌😁 {self.bot.user} is ready!")

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild: disnake.Guild):
        await self.bot.change_presence(activity=disnake.Game(
            name=f"{len(self.bot.guilds):,} guilds | {len(self.bot.users):,} members"
        ))

    @commands.Cog.listener()
    async def on_guild_leave(self, guild: disnake.Guild):
        await self.bot.change_presence(activity=disnake.Game(
            name=f"{len(self.bot.guilds):,} guilds | {len(self.bot.users):,} members"
        ))


def setup(bot):
    bot.add_cog(Events(bot))
