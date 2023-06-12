import random
import time

import disnake
import poe
from disnake import Embed
from disnake.ext import commands

from client import DiscordBotClient
from config import Config, Errbed
from modules.buttons import Completed, HistoryPaginator
from modules.localization import Localization

models = {
    'claude-v1': 'a2_2',
    'claude-instant': 'a2',
    'claude-instant-100k': 'a2_100k',
    'sage': 'capybara',
    'gpt-4': 'beaver',
    'gpt-3.5-turbo': 'chinchilla',
}


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBotClient = bot
        self.bot.i18n.load("./localization/")

    @commands.slash_command(
        name="gpt",
        description=disnake.Localized(
            "Use one of the following GPT text models",
            key="ask_description"
        )
    )
    async def gpt(
            self,
            interaction: disnake.ApplicationCommandInteraction
    ):
        pass

    @gpt.sub_command(
        name="ask",
        description=disnake.Localized(
            "Use one of the following GPT text models",
            key="ask_description"
        )
    )
    async def gpt_ask(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            prompt: str = commands.Param(
                name="prompt",
                description=disnake.Localized(
                    "Enter the text of your query",
                    key="ask_prompt_description"
                ),
                min_length=1
            ),
            model=commands.Param(
                name="model",
                description=disnake.Localized(
                    "Choose one of the proposed models you want to use",
                    key="ask_model_description"
                ),
                choices=list(models.keys()),
                default=None
            )
    ):

        await interaction.response.defer()
        start_time = time.time()

        try:
            model = model or dict(await self.bot.database.get_user_datas(interaction.author.id))["model"]

            base = f'*model*: `{model}`\n'
            system = 'system: your response will be rendered in a discord message, include language hints when ' \
                     'returning code like: ```py ...```, and use * or ** or > to create highlights ||\n prompt:'

            token = random.choice(open('data/tokens.txt', 'r').read().splitlines())
            client = poe.Client(
                token=token.split(":")[0],
                # proxy=self.file_proxier.get_random_proxy()
            )

            await interaction.edit_original_response(base)
            self.bot.loop.create_task(self.bot.database.add_number_of_requests(interaction.author.id))

            base += '\n'

            completion = client.send_message(
                models[model],
                system + prompt,
                with_chat_break=True
            )

            index = 0

            for token in completion:
                base += token['text_new']
                base = base.replace('Discord Message:', '')

                if index >= 5:
                    index = 0
                    await interaction.edit_original_response(content=base)

                index += 1
            await interaction.edit_original_response(content=base, components=[Completed(start_time)])

            original_message = await interaction.original_message()
            await self.bot.database.insert_request_to_history(
                user_id=interaction.author.id,
                prompt=prompt,
                answer=base.strip().lstrip(f"*model:* `{model}`").strip("\n"),
                model=model,
                jump_url=original_message.jump_url
            )
            await self.bot.database.add_generated_characters(interaction.author.id, len(base) - 18)

        except Exception as e:
            await interaction.edit_original_response(
                embed=Errbed(f"`{e.__class__.__name__}`: `{e}`", "⚠️ Contact the developer (/bot)")
            )

        await self.bot.database.add_times_of_use_commands(interaction.author.id)

    @gpt.sub_command(
        name="set-engine",
        description=disnake.Localized(
            "Set the default model (default: gpt-4)",
            key="ask_set_engine_description"
        )
    )
    async def ask_set_engine(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            model: str = disnake.Option(
                name="model",
                description=disnake.Localized(
                    "Select one of the models you want to use by default",
                    key="ask_set_engine_model_description"
                ),
                choices=list(models.keys()),
                required=True
            )
    ):
        await interaction.response.defer()

        language = await self.bot.localization.get_language(interaction.author.id)
        await self.bot.database.set_default_model(interaction.author.id, model)

        await interaction.edit_original_response(embed=disnake.Embed(
            color=Config.config()["COLOR"]
        ).set_author(
            name=self.bot.localization.get("ask_set_engine_embed_author_name", language).format(model=model),
            icon_url=interaction.author.display_avatar.url
        ))
        await self.bot.database.add_times_of_use_commands(interaction.author.id)

    @gpt.sub_command(
        name="history",
        description=disnake.Localized(
            "Get your request history",
            key="gpt_history_description"
        )
    )
    async def gpt_history(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            user: disnake.User = commands.Param(
                name="user",
                description=disnake.Localized(
                    "Mention a user to view their request history",
                    key="gpt_history_user_description"
                ),
                default=None
            )
    ):
        await interaction.response.defer()

        user = user or interaction.user
        language = await self.bot.localization.get_language(interaction.author.id)
        history = dict(await self.bot.database.get_user_datas(user.id))["history"]
        parsing = lambda _: f"<t:{_['created_at']}:R>: **[" + (_['prompt'].replace('*', '').replace('\n', '') if len(
            _['prompt'].replace('*', '').replace('\n', '')) <= 32 else _['prompt'].replace('*', '').replace('\n', '')[
                                                                       :30] + "...") + f"]({_['jump_url']})**"

        pages = list(map(parsing, history))
        paginator = HistoryPaginator(interaction, bot=self.bot, pages=pages)

        if not [0]:  # description:
            return await interaction.edit_original_response(embed=Errbed(
                self.bot.localization.get("gpt_history_errbed_description", language)
            ))

        embed = disnake.Embed(
            color=Config.config()["COLOR"]
        ).set_author(
            name=self.bot.localization.get("gpt_history_embed_author_name", language).format(user=user),
            icon_url=user.display_avatar.url
        )

        await interaction.edit_original_response(embed=embed, view=paginator)
        await paginator.init()

    @commands.slash_command(
        name="bot",
        description=disnake.Localized(
            "See all information about the bot",
            key="bot_description"
        )
    )
    async def information(
            self,
            interaction: disnake.ApplicationCommandInteraction
    ):
        language = await self.bot.localization.get_language(interaction.author.id)

        application_info = await self.bot.application_info()
        commands_count = len(self.bot.slash_commands) + len(
            list(filter(lambda _: _.hidden is False, self.bot.commands)))

        embed = Embed(
            description=self.bot.localization.get("bot_embed_description", language).format(bot_user=self.bot.user),
            color=Config.config()["COLOR"]
        ).add_field(
            name=self.bot.localization.get("bot_embed_field_0_name", language),
            value="\n".join((
                self.bot.localization.get("bot_embed_field_0_value_0", language).format(
                    guilds_count=f"{len(self.bot.guilds):,}"),
                self.bot.localization.get("bot_embed_field_0_value_1", language).format(
                    members_count=f"{len(self.bot.users):,}"),
                self.bot.localization.get("bot_embed_field_0_value_2", language).format(commands_count=commands_count)
            )),
            inline=False
        ).add_field(
            name=self.bot.localization.get("bot_embed_field_1_name", language),
            value="\n".join((
                self.bot.localization.get("bot_embed_field_1_value_0", language).format(
                    time_of_use_commands=f"{await self.bot.database.get_sum_of_key('time_of_use_commands'):,}"),
                self.bot.localization.get("bot_embed_field_1_value_1", language).format(
                    number_of_requests=f"{await self.bot.database.get_sum_of_key('number_of_requests'):,}"),
                self.bot.localization.get("bot_embed_field_1_value_2", language).format(
                    generated_characters=f"{await self.bot.database.get_sum_of_key('generated_characters'):,}")
            )),
            inline=False
        ).add_field(
            name=self.bot.localization.get("bot_embed_field_2_name", language),
            value="\n".join((
                self.bot.localization.get("bot_embed_field_2_value_0", language).format(
                    application_info_owner=application_info.owner,
                    application_info_owner_id=application_info.owner.id
                ),
                self.bot.localization.get("bot_embed_field_2_value_1", language)
            )),
            inline=False
        ).set_author(
            name=self.bot.user,
            icon_url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )
        await self.bot.database.add_times_of_use_commands(interaction.author.id)

    @commands.slash_command(
        name="user",
        description=disnake.Localized(
            "Information about you or a selected user",
            key="user_description"
        )
    )
    async def user(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            user: disnake.User = commands.Param(
                name="user",
                description=disnake.Localized(
                    "Mention a user to view information about them",
                    key="user_user_description"
                ),
                default=None,
                min_length=1
            )
    ):
        language = await self.bot.localization.get_language(interaction.author.id)

        user = user or interaction.author
        arrow = "<:qt_green_arrow:1116780116215865385>"

        if user.bot is True:
            return await interaction.response.send_message(
                embed=Errbed(self.bot.localization.get("user_errbed_description", language)),  # user_errbed_description
                ephemeral=True
            )

        document = await self.bot.database.get_user_datas(user.id)

        created_at = f"<t:{document['created_at']}{':R>' if (time.time() - document['created_at']) <= 86400 else '>'}"

        embed = Embed(
            description=self.bot.localization.get("user_embed_description", language),  # user_embed_description
            color=Config.config()["COLOR"]
        ).add_field(
            name=self.bot.localization.get("user_embed_field_0_name", language).format(arrow=arrow),
            # user_embed_field_0_name | arrow=arrow
            value="\n".join((
                self.bot.localization.get("user_embed_field_0_value_0", language).format(
                    time_of_use_commands=f"{document['time_of_use_commands']:,}"),
                # user_embed_field_0_value_0 | time_of_use_commands=f"{document['time_of_use_commands']:,}"
                self.bot.localization.get("user_embed_field_0_value_1", language).format(
                    number_of_requests=f"{document['number_of_requests']:,}"),
                self.bot.localization.get("user_embed_field_0_value_2", language).format(
                    generated_characters=f"{document['generated_characters']:,}")
            )),
            inline=False
        ).add_field(
            name=self.bot.localization.get("user_embed_field_1_name", language).format(arrow=arrow),
            # user_embed_field_1_name | arrow=arrow
            value=self.bot.localization.get("user_embed_field_1_value_0", language).format(created_at=created_at)
            # user_embed_field_1_value_0 | created_at=created_at
        ).set_author(
            name=self.bot.localization.get("user_embed_author_name", language).format(user=user),
            # user_embed_author_name | user=user
            icon_url=user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)
        await self.bot.database.add_times_of_use_commands(interaction.author.id)

    @commands.slash_command(
        name="help",
        description=disnake.Localized(
            "List of all available bot commands",
            key="help_description"
        )
    )
    async def help(
            self,
            interaction: disnake.ApplicationCommandInteraction
    ):
        language = await self.bot.localization.get_language(interaction.author.id)
        arrow = "<:qt_green_arrow:1116780116215865385>"

        embed = Embed(
            color=Config.config()["COLOR"]
        ).add_field(
            name=self.bot.localization.get("help_embed_field_0_name", language).format(arrow=arrow),
            value="`/ping`, `/bot`, `/user`",
            inline=False
        ).add_field(
            name=self.bot.localization.get("help_embed_field_1_name", language).format(arrow=arrow),
            value="`/ask`",
            inline=False
        ).set_author(
            name=self.bot.user,
            icon_url=self.bot.user.display_avatar.url
        ).set_thumbnail(
            url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)
        await self.bot.database.add_times_of_use_commands(interaction.author.id)

    @commands.slash_command(
        name="ping",
        description=disnake.Localized(
            "The bot ping",
            key="ping_description"
        )
    )
    async def ping(
            self,
            interaction: disnake.ApplicationCommandInteraction
    ):
        language = await self.bot.localization.get_language(interaction.author.id)
        await interaction.response.send_message(
            self.bot.localization.get("ping_content", language).format(bot_latency=round(self.bot.latency * 1000, 1))
        )
        await self.bot.database.add_times_of_use_commands(interaction.author.id)

    @commands.slash_command(
        name="set-language",
        description=disnake.Localized(
            "Set the bot language",
            key="set_language_description"
        )
    )
    async def set_language(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            language: str = commands.Param(
                name="language",
                description=disnake.Localized(
                    "Select the language you want to set for yourself in the bot interface",
                    key="set_language_language_description"
                ),
                choices=Localization.allowed_languages()
            )
    ):
        await interaction.response.defer()
        await self.bot.localization.set_user_language(interaction.author.id, language)
        await self.bot.database.add_times_of_use_commands(interaction.author.id)
        await interaction.edit_original_response(embed=disnake.Embed(
            color=Config.config()["COLOR"]
        ).set_author(
            name=self.bot.localization.get("set_language_embed_author_name", language).format(language=language),
            icon_url=interaction.author.display_avatar.url
        ))


def setup(bot):
    bot.add_cog(Commands(bot))
