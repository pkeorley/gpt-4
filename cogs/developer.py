from disnake.ext import commands


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog_name: str = None):
        extensions = list(map(
            lambda _: "cogs." + self.bot.cogs[_].qualified_name.lower(),
            list(self.bot.cogs.keys())
        ))

        if cog_name:
            extensions = ["cogs." + cog_name]

        log = []

        for extension in extensions:
            try:
                self.bot.reload_extension(extension)
                log.append(f"✅ {extension}")
            except Exception as error:
                log.append(f"⛔ {extension} （￣︶￣）↗　`{error}`")

        await ctx.reply("\n".join(log))
        await self.bot.add_times_of_use_commands(ctx.author.id)


def setup(bot):
    bot.add_cog(Developer(bot))
