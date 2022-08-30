import shutil
import os
import sys
import time

import servicemanager
from loguru import logger as log
from typing import NamedTuple
from datetime import datetime
from archive import Compression
from config import openConfig
from utils import getArchive, getCreateDate, deleteArchive, getDir, setDateCreationModificationAccess
from winservice import SMWinservice


class NotWorkTime(NamedTuple):
    start: int
    end: int


def handlerErrorDelDirTree(func, path, _):
    import stat
    os.chmod(path, stat.S_IWUSR)
    func(path)


def worker():
    config = openConfig()
    udsp = os.path.normpath(config.get("Settings", "user_data_storage_path").strip("\""))
    if not udsp:
        log.critical("Не указана директория с профилями.")
        exit(1)
    log.add(os.path.join(udsp, "work_service.log"), level="DEBUG", rotation="10 MB",
            format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")
    not_work_time = None
    try:
        not_work_time = NotWorkTime(
            *[int(x.strip()) for x in config.get("Settings", "not_work_time_interval").split("-")]
        )
    except (TypeError, ValueError):
        log.critical("Ошибка чтения конфиг файла, параметр: not_work_time.")
        exit(1)
    storage_time_in_days = None
    try:
        storage_time_in_days = int(config.get("Settings", "storage_time_in_days"))
    except (TypeError, ValueError):
        log.critical("Ошибка чтения конфиг файла, параметр: storage_time_in_days.")
        exit(1)

    for arch in getArchive(udsp):
        create_time = getCreateDate(os.path.join(udsp, arch))
        storage_time = datetime.now() - create_time
        log.debug(f"{arch} - в хранилище {storage_time.days} д.")
        if storage_time.days > storage_time_in_days:
            deleteArchive(os.path.join(udsp, arch), udsp)

    date_now = datetime.now()
    if date_now.hour < not_work_time.start or date_now.hour > not_work_time.end:
        for dir_name in getDir(udsp):
            if os.path.exists(os.path.join(udsp, dir_name) + ".7z"):
                log.debug(f"Запуск удаления директории: {dir_name}")
                shutil.rmtree(os.path.join(udsp, dir_name), ignore_errors=False, onerror=handlerErrorDelDirTree)
                continue
            log.debug(f"Подготовка к архивации директории: {dir_name}")
            archive = Compression()
            archive.setDataPath(os.path.join(udsp, dir_name))
            # archive.setProgressCallBack(lambda x: log.info(f"Прогресс: {x}%"))
            _stat = archive.compression(archive_path=os.path.join(udsp, dir_name) + ".7z")
            log.info(_stat.compressionLevel())
            create_time = getCreateDate(os.path.join(udsp, dir_name))
            setDateCreationModificationAccess(os.path.join(udsp, _stat.name), create_time)
            log.debug(f"Запуск удаления директории: {dir_name}")
            shutil.rmtree(os.path.join(udsp, dir_name), ignore_errors=True)


class Service(SMWinservice):
    _isRunning = False

    def __init__(self, args):
        super().setName("UserDataStorage")
        super().setDisplayName("User Data Storage")
        super().setDescription("User Data Storage")
        super().__init__(args)

    def start(self):
        self._isRunning = True

    def stop(self):
        self._isRunning = False

    def main(self):
        while self._isRunning:
            datetime_now = datetime.now()
            if datetime_now.minute == 0 and datetime_now.second == 0:
                worker()
            time.sleep(1)


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        os.chdir(application_path)
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(Service)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        Service.parse_command_line()
