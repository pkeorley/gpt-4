import disnake
from disnake.ext import commands

from client import DiscordBotClient
from modules.evalec import execute_code


class Eval(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBotClient = bot

    @commands.command(
        name="e",
        aliases=["eval"],
        description="Execute python code in Discord",
        hidden=True
    )
    @commands.is_owner()
    async def e(
            self,
            ctx: commands.Context,
            *,
            code: str
    ):
        try:
            result = await execute_code(code.strip("`").lstrip("py"), {
                "disnake": disnake,
                "commands": commands,
                "ctx": ctx,
                "bot": self.bot
            })
            if "await ctx." not in ",".join(code.split("\n")[-2:-1]):
                await ctx.reply(f"```py\n{result}```")
        except Exception as e:
            await ctx.reply(f"```py\n{e.__class__.__name__}: {e}```")

        await self.bot.add_times_of_use_commands(ctx.author.id)


def setup(bot):
    bot.add_cog(Eval(bot))
