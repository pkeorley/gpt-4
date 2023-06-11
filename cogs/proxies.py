from typing import Union

import aiohttp
import disnake
from disnake.ext import commands


async def get_proxies(limit: int = 10, page: int = 1, protocols: str = "socks5,socks4,http,https",
                      country: Union[str, int, bool] = "US"):
    url = f"https://proxylist.geonode.com/api/proxy-list?limit={limit}&page={page}&sort_by=lastChecked&sort_type=desc"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            j = await response.json()

            protocols = list(map(lambda _: _.strip().lower(),
                                 protocols.split(","))) if "," in protocols else protocols.strip().lower()

            ips_ports = list(filter(
                lambda _: any(
                    protocol in protocols
                    for protocol in _.get("protocols")
                ) and all((
                    _.get("ip"),
                    _.get("port")
                )) and (_.get("country") == country if country else True),
                j["data"]
            ))

            configs = []
            for ip_port in ips_ports:
                configs.append({
                    "protocols": ip_port["protocols"],
                    "http": "http://{}:{}/".format(ip_port["ip"], ip_port["port"]),
                    "https": "https://{}:{}/".format(ip_port["ip"], ip_port["port"])
                })

            return configs


def split_text(text, chunk_size):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks


class Dropdown(disnake.ui.Select):
    def __init__(self, content: list):
        self.content = content
        options = [
            disnake.SelectOption(
                label=str(page_number),
                emoji="📚"
            )
            for page_number in range((len(self.content) // 10) - 1)
        ]

        super().__init__(
            placeholder="Select the page you want to go to...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        values = int(self.values[0])
        await inter.edit_original_response(
            content="\n".join(self.content[(values * 10) - 10:values * 10])
        )


class Proxies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="proxies", description="Get proxies by your settings")
    async def proxies(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            limit: commands.Range[1, 500] = 1,
            page: commands.Range[1, 5] = 1,
            protocols: str = commands.Param(
                default="socks5,socks4,http,https",
                description="Enter the protocols with a comma between each, default: socks5,socks4,http,https"
            ),
            country: str = commands.Param(
                min_length=2,
                max_length=2,
                default="US",
                description="Put the code of country, examples: BR, US, UK, UA and etc."
            )
    ):
        await interaction.response.defer()

        proxies = await get_proxies(
            limit=limit,
            page=page,
            protocols=protocols,
            country=country.upper()
        )

        content = []

        for proxy in proxies:
            content.append("(`{}`) | [`https`]({}) / [`http`]({})".format(
                "/".join(p.upper() for p in proxy["protocols"]),
                proxy["https"],
                proxy["http"]
            ))

        if not content:
            return await interaction.edit_original_response(
                content="⛔ We do not found any IPs"
            )

        view = disnake.ui.View()
        view.add_item(Dropdown(content))

        await interaction.edit_original_response(
            content="\n".join(content[:10]),
            view=view
        )


def setup(bot):
    ...
    #  bot.add_cog(Proxies(bot))
