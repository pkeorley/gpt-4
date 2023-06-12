from typing import List

import disnake
from disnake.ext import commands

from modules.database import Database
from modules.localization import Localization

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True


class DiscordBotClient(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=disnake.Intents.all(),
            command_sync_flags=command_sync_flags
        )

        self.localization: Localization = Localization(self)
        self.database = Database(self)

    async def get_prefix(self, message: disnake.Message) -> List[str]:
        return ["!", "b."]

