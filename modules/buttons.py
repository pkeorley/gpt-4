import asyncio
import time
from typing import List, Any

import disnake

from client import DiscordBotClient
from config import Errbed


class Completed(disnake.ui.Button):
    def __init__(self, start_time: float):
        super().__init__(
            label=f"Completed as {round(time.time() - start_time, 2)}s.",
            emoji="✅",
            style=disnake.ButtonStyle.green,
            disabled=True
        )


class HistoryPaginator(disnake.ui.View):
    def __init__(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            bot: DiscordBotClient,
            pages: List[Any]
    ):
        super().__init__(
            timeout=360.0
        )
        self.interaction = interaction
        self.bot: DiscordBotClient = bot
        self.pages = pages
        self.parsed_items = [
            (item, (item + 15 if item + 15 < len(self.pages) else len(self.pages)))
            for item in list(range(0, len(self.pages), 15))
        ]
        self.descriptions = [self.pages[x:y] for x, y in self.parsed_items]
        self.index = 0
        self.bot.loop.create_task(self.disable_buttons())

    async def disable_buttons(self):
        await asyncio.sleep(360)

        self.to_left.disabled = True
        self.reset_page.disabled = True
        self.to_right.disabled = True

        await self.interaction.edit_original_response(view=self)

    async def init(self):
        embed = await self._generate_embed()
        await self.interaction.edit_original_response(embed=embed)

    async def _generate_embed(self):
        original_message = await self.interaction.original_message()
        embed: disnake.Embed = original_message.embeds[0]

        index = self.parsed_items[self.index]

        embed.description = "\n".join(self.pages[index[0]:index[1]])
        embed.set_footer(
            text=f"Pages: {self.index + 1:,}/{len(self.parsed_items):,}",
            icon_url="https://images.emojiterra.com/twitter/512px/1f4c4.png"
        )

        return embed

    async def check(self, interaction: disnake.ApplicationCommandInteraction):
        language = await self.bot.localization.get_language(interaction.author.id)

        return {
            "status": interaction.author.id == self.interaction.author.id,
            "error": self.bot.localization.get("history_paginator_check_error", language)
        }

    @disnake.ui.button(
        emoji="⬅️",
        style=disnake.ButtonStyle.blurple
    )
    async def to_left(
            self,
            button: disnake.Button,
            interaction: disnake.ApplicationCommandInteraction
    ):
        await interaction.response.defer()

        check = await self.check(interaction)
        if not check.get("status"):
            return interaction.response.send_message(
                embed=Errbed(check.get("error")),
                ephemeral=True
            )

        if self.index > 0:
            self.index -= 1
        await self.interaction.edit_original_response(
            embed=await self._generate_embed()
        )

    @disnake.ui.button(
        emoji="🔁",
        style=disnake.ButtonStyle.red
    )
    async def reset_page(
            self,
            button: disnake.Button,
            interaction: disnake.ApplicationCommandInteraction
    ):
        await interaction.response.defer()

        check = await self.check(interaction)
        if not check.get("status"):
            return interaction.response.send_message(
                embed=Errbed(check.get("error")),
                ephemeral=True
            )

        self.index = 0
        await self.interaction.edit_original_response(
            embed=await self._generate_embed()
        )

    @disnake.ui.button(
        emoji="➡️",
        style=disnake.ButtonStyle.blurple
    )
    async def to_right(
            self,
            button: disnake.Button,
            interaction: disnake.ApplicationCommandInteraction
    ):
        await interaction.response.defer()

        check = await self.check(interaction)
        if not check.get("status"):
            return interaction.response.send_message(
                embed=Errbed(check.get("error")),
                ephemeral=True
            )

        if self.index <= len(self.parsed_items):
            self.index += 1
        await self.interaction.edit_original_response(
            embed=await self._generate_embed()
        )


