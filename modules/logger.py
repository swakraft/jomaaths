import inspect
from datetime import datetime

class DisplaySettings:
    def __init__(self, show_date: bool = True, show_hour: bool = True, show_caller: bool = True):
        self.show_date = show_date
        self.show_hour = show_hour
        self.show_caller = show_caller

class Logger:
    def __init__(self, display_settings:DisplaySettings = DisplaySettings()):
        self.display_settings = display_settings

    def __formatter__(self, datetime:datetime):
        show_date = self.display_settings.show_date
        show_hour = self.display_settings.show_hour

        if not show_date and not show_hour:
            return ''
        
        elif show_date and show_hour:
            return f'{0 if datetime.day < 10 else ""}{datetime.day}/{0 if datetime.month < 10 else ""}{datetime.month}/{datetime.year} à {0 if datetime.hour < 10 else ""}{datetime.hour}:{0 if datetime.minute < 10 else ""}{datetime.minute}:{0 if datetime.second < 10 else ""}{datetime.second} '
        
        elif show_date:
            return f'{0 if datetime.day < 10 else ""}{datetime.day}/{0 if datetime.month < 10 else ""}{datetime.month}/{datetime.year} '
        
        elif show_hour:
            return f'{0 if datetime.hour < 10 else ""}{datetime.hour}:{0 if datetime.minute < 10 else ""}{datetime.minute}:{0 if datetime.second < 10 else ""}{datetime.second} '

    def info(self, *content: str):
        if self.display_settings.show_caller:
            caller = inspect.stack()[1][3]
            caller = (caller + ":") if caller != '<module>' else 'main thread:'
            caller = "\33[0;96m " + caller + "\33[0;96m "
    
        else:
            caller = "\033[0;0m "
        
        t = ''
        for i in content:
            t +=  str(i) + ' '

        print("\33[90m" + self.__formatter__(datetime.now()) + "\033[1;32;40m[INFO]" + caller + "\033[0;0m" + str(t.strip()))
    
    def warn(self, *content: str):
        if self.display_settings.show_caller:
            caller = inspect.stack()[1][3]
            caller = (caller + ":") if caller != '<module>' else 'main thread:'
            caller = "\33[0;96m " + caller + "\33[0;96m "
    
        else:
            caller = "\033[0;0m "

        t = ''
        for i in content:
            t +=  str(i) + ' '

        print("\33[90m" + self.__formatter__(datetime.now()) + "\033[1;33;40m[WARN]" + caller + "\033[0;0m" + str(t.strip()))
    
    def crit(self, *content: str):
        if self.display_settings.show_caller:
            caller = inspect.stack()[1][3]
            caller = (caller + ":") if caller != '<module>' else 'main thread:'
            caller = "\33[0;96m " + caller + "\33[0;96m "
    
        else:
            caller = "\033[0;0m "

        t = ''
        for i in content:
            t +=  str(i) + ' '
        
        print("\33[90m" + self.__formatter__(datetime.now()) + "\033[1;31;40m[CRIT]" + caller + "\033[0;0m" + str(t.strip()))
    
    def debug(self, *content: str):
        if self.display_settings.show_caller:
            caller = inspect.stack()[1][3]
            caller = (caller + ":") if caller != '<module>' else 'main thread:'
            caller = "\33[0;96m " + caller + "\33[0;96m "
    
        else:
            caller = "\033[0;0m "

        t = ''
        for i in content:
            t +=  str(i) + ' '
            
        print("\33[90m" + self.__formatter__(datetime.now()) + "\033[1;95;40m[DEBUG]" + caller + "\033[0;0m" + str(t.strip()))