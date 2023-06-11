from disnake import Embed
from dotenv import dotenv_values


class Config:
    PATH = r"venv\.env"

    @classmethod
    def config(cls):
        return {
            **dotenv_values(cls.PATH),
            "LOADING_EMOJI": "<a:qt_typing:1075772998746918912>",
            "COLOR": 0x51d84b,
            "ERROR_COLOR": 0xec2828
        }


def Errbed(description: str, footer_text: str = None, author_name: str = None, author_icon_url: str = None):
    embed = Embed(
        description=description,
        color=Config.config()["ERROR_COLOR"]
    )
    embed.set_author(
        name=author_name or "An error has occurred",
        icon_url=author_icon_url or "https://cdn.discordapp.com/emojis/897059435254530099.gif?size=4096&quality"
                                    "=lossless"
    )

    if footer_text:
        embed.set_footer(
            text=footer_text
        )

    return embed
