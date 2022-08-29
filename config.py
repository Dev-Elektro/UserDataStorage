import os
from configparser import ConfigParser


def createConfig(path: str = None):
    """Создание файла конфигурации"""
    config = ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "user_data_storage_path", "")
    config.set("Settings", "not_work_time_interval", "8-17")
    config.set("Settings", "storage_time_in_days", "90")

    with open(path, "w", encoding='utf-8') as config_file:
        config.write(config_file)


def openConfig(path: str = None) -> ConfigParser:
    """Загрузить конфиг, если файла нет создать."""
    if not path:
        path = os.path.join(os.path.abspath(os.curdir), "config.ini")  # Путь к файлу настроек по умолчанию.
    if not os.path.exists(path):  # Если файл отсутствует, то создаем его.
        createConfig(path)
    config = ConfigParser()
    config.read(path, encoding='utf-8')
    return config
