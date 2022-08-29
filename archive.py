import os
import io
import subprocess
from loguru import logger as log
import re
from dataclasses import dataclass
from typing import Callable


@dataclass
class ArchiveStat:
    name: str = None
    folder: int = -1
    files: int = -1
    size: int = -1
    archiveSize: int = -1

    def compressionLevel(self) -> int:
        return self.size - self.archiveSize


class Compression:
    """Сжатие директории при помощи архиватора 7z.\n
    setExePath(path: str) - путь к исполняемому файлу 7z.exe\n
    setDataPath(path: str) - путь к директории с файлами для сжатия\n
    setProgressCallBack(cb: Callable) - обратный вызов для отображения прогресса сжатия\n
    compression(archive_path: str) - запуск процесса сжатия с указанием пути к архиву с расширением"""
    def __init__(self):
        self._progress_cb = None
        self._data_path = None
        self._file_path = r"C:\Program Files\7-Zip\7z.exe"

    def setExePath(self, path: str) -> None:
        """Путь к исполняемому файлу 7z.exe"""
        self._file_path = os.path.abspath(path)

    def setDataPath(self, path: str) -> None:
        """Путь к директории с файлами для сжатия"""
        self._data_path = os.path.abspath(path)

    def setProgressCallBack(self, cb: Callable) -> None:
        """Обратный вызов для отображения прогресса сжатия. callback(progress: int)"""
        self._progress_cb = cb

    def compression(self, *, archive_path: str) -> ArchiveStat:
        """Сжатие директории"""
        if not all([archive_path, self._data_path]):
            raise ValueError
        archive_stat = ArchiveStat(name=os.path.basename(archive_path))
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        with subprocess.Popen([self._file_path, "-bsp1", "a", "-ssw", "-mx4", "-r0", archive_path, self._data_path],
                              cwd=os.path.abspath(os.path.dirname(self._file_path)),
                              startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              stdin=subprocess.DEVNULL) as proc:
            progress = None
            for line in io.TextIOWrapper(proc.stdout, encoding="cp866"):
                res = re.findall(r"^(\d+)\s\w+,\s(\d+)\s\w+,\s(\d+)\s.+$", line)
                if res:
                    archive_stat.folder = res[0][0]
                    archive_stat.files = res[0][1]
                    archive_stat.size = int(res[0][2])
                    log.debug(archive_stat)
                res = re.findall(r"^\s*(\d+)%.*$", line)
                if res:
                    if progress == res[0]:
                        continue
                    progress = res[0]
                    if not isinstance(self._progress_cb, type(None)):
                        self._progress_cb(progress)
                res = re.findall(r"^Archive size:\s(\d+)\sbytes.*$", line)
                if res:
                    archive_stat.archiveSize = int(res[0])
                    log.debug(archive_stat)
        return archive_stat
