import os


class Localization:
    def __init__(self, bot):
        self.bot = bot

    async def get_language(self, user_id: int):
        await self.bot.insert_user_if_not_exists(user_id)
        document = await self.bot.db.gpt4.find_one({"user_id": user_id})
        return (dict(document) or {}).get("language", "en_GB")

    async def set_user_language(self, user_id: int, language: str):
        await self.bot.insert_user_if_not_exists(user_id)
        await self.bot.db.gpt4.update_one({"user_id": user_id}, {"$set": {"language": language}})

    @classmethod
    def allowed_languages(cls):
        return [language.rstrip(".json") for language in os.listdir("./localization")]

    def get(self, key: str, language: str) -> str:
        return self.bot.i18n.get(key)[language.replace("_", "-")]
