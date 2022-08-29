import socket

import win32serviceutil
import servicemanager
import win32event
import win32service
import sys


class SMWinservice(win32serviceutil.ServiceFramework):
    """Base class to create winservice in Python"""
    _svc_name_ = 'UserDataStorage'
    _svc_display_name_ = 'User Data Storage'
    _svc_description_ = 'User Data Storage'

    @classmethod
    def parse_command_line(cls):
        """ClassMethod to parse the command line"""
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        """Constructor of the winservice"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        """Called when the service is asked to stop"""
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Called when the service is asked to start"""
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def setName(self, name: str) -> None:
        """Установка имени сервиса"""
        self._svc_name_ = name

    def setDisplayName(self, name: str) -> None:
        """Установка отображаемого имени сервиса"""
        self._svc_display_name_ = name

    def setDescription(self, name: str) -> None:
        """Установка описания сервиса"""
        self._svc_description_ = name

    def start(self):
        pass

    def stop(self):
        pass

    def main(self):
        pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SMWinservice)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        SMWinservice.parse_command_line()
