from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

load_dotenv()


class Settings(BaseSettings):
    """
    Конфигурация подключения к базе данных
    """

    db_url: str = "sqlite+aiosqlite:///./db.sqlite3"
    db_echo: bool = False

    """
    Конфигурация подключения к хранилищу
    STORAGE_PATH: путь к директории модулей
    SERVER_IP: ip адрес сервера хранилища
    SERVER_USER: имя пользователя сервера
    """
    STORAGE_PATH: str = "/home/aiven/offline_repo/packages"

    # STORAGE_PATH: str = "~/offline_repo/packages"

    SERVER_IP: str = os.getenv("SERVER_IP")
    SERVER_USER: str = os.getenv("SERVER_USER")

    # DIR2PI_PATH: str = "~/venv_pip2pi/bin/dir2pi"
    # SIMPLE_DIR: str = "~/offline_repo/packages/simple"

    DIR2PI_PATH: str = "/home/aiven/venv_pip2pi/bin/dir2pi"
    SIMPLE_DIR: str = "/home/aiven/offline_repo/packages/simple"


settings = Settings()
