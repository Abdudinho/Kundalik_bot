from dotenv import load_dotenv
from os import getenv

load_dotenv()


class BotToken:
    BOT_TOKEN = getenv('BOT_TOKEN')

class AdminEnv:
    _raw_ids = getenv("ADMIN_IDS", "")
    ADMIN_IDS = {int(x) for x in _raw_ids.replace(" ", "").split(",") if x.strip()}

class DatabaseEnv:
    DB_USER = getenv("DB_USER")
    DB_PASSWORD = getenv("DB_PASSWORD")
    DB_HOST = getenv("DB_HOST")
    DB_PORT = getenv("DB_PORT")
    DB_NAME = getenv("DB_NAME")
    DATABASE_URL = (
        f"postgresql+asyncpg://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}"
        f"@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
    )


class WebEnv:
    ADMIN_NAME = getenv("ADMIN_NAME")
    ADMIN_PASSWORD = getenv("ADMIN_PASSWORD")

class Env:
    bot = BotToken()
    db = DatabaseEnv()
    web = WebEnv()