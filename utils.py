import os
import re
from datetime import datetime
from typing import Optional
from loguru import logger as log
import filedate


def getDir(path: str) -> list:
    """Возвращает список директорий"""
    return [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]


def getArchive(path: str) -> list:
    """Возвращает список архивов *.7z"""
    return [x for x in os.listdir(path) if os.path.isfile(os.path.join(path, x)) and x[-3:] == ".7z"]


def getDateFromName(name: str) -> Optional[datetime]:
    """Получить дату из имени файла, если она там указана."""
    date_from_name = re.findall(r'\((\d{2}\.\d{2}\.\d{4})\)', name)
    if date_from_name:
        return datetime.strptime(date_from_name[0], "%d.%m.%Y")


def getCreateDate(path: str) -> datetime:
    """Получить дату создания файла"""
    create_time = getDateFromName(os.path.basename(path))
    if not create_time:
        create_time = datetime.fromtimestamp(os.path.getctime(path))
    return create_time


def setDateCreationModificationAccess(path: str, date: datetime) -> None:
    """Установить файлу дату создания, изменения и доступа"""
    os.utime(path, times=(date.timestamp(), date.timestamp()))
    filedate.File(path).set(created=date)


def deleteArchive(path: str, path_log: str) -> None:
    """Удаление архива данных и запись в лог удаления."""
    try:
        os.remove(path)
        with open(os.path.join(path_log, "Remote_archives_log.txt"), "a", encoding='utf-8') as flog:
            flog.write(f"Архив '{os.path.basename(path)}' - удален: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.debug(f"Архив '{os.path.basename(path)}' - удален: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except OSError as e:
        log.warning(f"Ошибка удаления: {path} - {e.strerror}")
