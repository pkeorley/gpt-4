from motor.motor_asyncio import AsyncIOMotorClient

from client import DiscordBotClient
from config import Config


class Database:
    def __init__(
            self,
            bot: DiscordBotClient
    ):
        self.bot = bot
        self.cluster = AsyncIOMotorClient(Config.config()["MONGO_URL"])
        self.db = self.cluster.website

    async def insert_user_if_not_exists(self, user_id: int):
        """
        Додати користувача в базу даних якщо він відсутній
        :param user_id: Індифікатор користувача
        :return: None
        """
        if await self.db.gpt4.count_documents({"user_id": user_id}) == 0:
            await self.db.gpt4.insert_one({
                "user_id": user_id,
                "created_at": round(time.time()),
                "time_of_use_commands": 0,
                "number_of_requests": 0,
                "generated_characters": 0,
                "language": "en_GB",
                "model": "gpt-4",
                "history": []
            })

    async def insert_request_to_history(self, user_id: int, prompt: str, answer: str, model: str, jump_url: str):
        await self.insert_user_if_not_exists(user_id)
        history = {
            "prompt": prompt,
            "answer": answer,
            "model": model,
            "jump_url": jump_url,
            "created_at": round(time.time())
        }
        await self.db.gpt4.update_one({
            "user_id": user_id
        }, {
            "$push": {
                "history": history
            }
        })
        return history

    async def set_default_model(self, user_id: int, model: str):
        await self.insert_user_if_not_exists(user_id)
        await self.db.gpt4.update_one({"user_id": user_id}, {"$set": {"model": model}})

    async def get_user_datas(self, user_id: int):
        """
        Отримати документ користувача
        :param user_id: Індифікатор користувача
        :return: Dict[str, Any]
        """
        await self.insert_user_if_not_exists(user_id)
        return await self.db.gpt4.find_one({"user_id": user_id})

    async def inc_number_to_key(self, user_id: int, key: str, count: int):
        """
        Додати змінну `count` до ключа `key` для користувача `user_id`
        :param user_id: Індифікатор користувача
        :param key: Ключ до якого хочете додати `count`
        :param count: Кількість
        :return: None
        """
        await self.insert_user_if_not_exists(user_id)
        await self.db.gpt4.update_one({
            "user_id": user_id
        }, {
            "$inc": {
                key: count
            }
        })

    async def add_times_of_use_commands(self, user_id: int, count: int = 1):
        """
        Додати кількість разів використань команд для користувача
        :param user_id: Індифікатор користувача
        :param count: Кількість використань
        :return: None
        """
        await self.inc_number_to_key(user_id, "time_of_use_commands", count)

    async def add_number_of_requests(self, user_id: int, count: int = 1):
        """
        Додати кількість використань слеш-команди /ask
        :param user_id: Індифікатор користувача
        :param count: Кількість використань
        :return: None
        """
        await self.inc_number_to_key(user_id, "number_of_requests", count)

    async def add_generated_characters(self, user_id: int, count: int = 1):
        """
        Додати кількість згенерованих символів користувачем
        :param user_id: Індифікатор користувача
        :param count: Кількість використань
        :return: None
        """
        await self.inc_number_to_key(user_id, "generated_characters", count)

    async def delete_user(self, user_id: int):
        """
        Видалити користувача з бази данних
        :param user_id: Індифікатор користувача
        :return: None
        """
        await self.db.gpt4.delete_one({"user_id": user_id})

    async def get_sum_of_key(self, key: str):
        all_key_values = await self.db.gpt4.find({}).sort(key, -1).to_list(None)
        return sum(list(map(lambda _: _.get(key, 0), all_key_values)))
