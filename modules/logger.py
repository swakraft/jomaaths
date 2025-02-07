import inspect
from datetime import datetime
from typing import Any

class Line:
    def __init__(self, timestamp: str, color_code: str, level: str, caller_info: str, content: tuple[str], line: int, log: 'Logger') -> None:
        self._timestamp = timestamp
        self._color_code = color_code
        self._level = level
        self._caller_info = caller_info
        self._content = content
        self._line = line
        self._log = log
    
    def _move_cursor_up(self, n):
        print(f"\033[{n}A", end='')

    def _move_cursor_down(self, n):
        print(f"\033[{n}B", end='')
    
    def _clear_line(self):
        print("\033[K", end='')
    
    def add_text(self, *content):
        self._content += content
    
    def set_text(self, *content):
       self._content = content

    def _edit(self):
        n = self._log.curent_line - self._line + 1
        self._move_cursor_up(n)
        self._clear_line()
        message = ' '.join(map(str, self._content))
        text = f"\33[90m{self._timestamp}\033[1;{self._color_code};40m[{self._level}]{self._caller_info}\033[0;0m {message}"
        print(text)
        self._move_cursor_down(n)

    def edit_print(self):
        self._edit()
    
    def info(self):
        self._level = 'INFO'
        self._color_code = '32'
        self._edit()

    def warn(self):
        self._level = 'WARN'
        self._color_code = '33'
        self._edit()

    def crit(self):
        self._level = 'CRIT'
        self._color_code = '31'
        self._edit()

    def debug(self):
        self._level = 'DEBUG'
        self._color_code = '95', 
        self._edit()

    def get(self):
        self._level = 'GET'
        self._color_code = '38;5;30'
        self._edit()

    def post(self):
        self._level = 'POST'
        self._color_code = '38;5;202'
        self._edit()


class Logger:
    def __init__(self):
        self.curent_line = 0
        self.lines: list[str] = []

    def _formatter(self, datetime_obj: datetime) -> str:
        date_str = datetime_obj.strftime('%d/%m/%Y')
        hour_str = datetime_obj.strftime('%H:%M:%S')
        return f'{date_str} à {hour_str} '

    def log(self, level: str, color_code: str, *content: Any):
        if level not in ['GET', 'POST']:
            frame = inspect.stack()[2]
            caller = frame.function if frame.function != '<module>' else 'Main thread'
            filename = frame.filename.split('/')[-1]  # Just the file name, not the full path
            lineno = frame.lineno
            caller_info = f"{filename}:{lineno} {caller}"
            caller_info = f"\33[0;96m {caller_info}\33[0;96m"
        
        else:
            caller_info = ''

        message = ' '.join(map(str, content))
        timestamp = self._formatter(datetime.now())
        text = f"\33[90m{timestamp}\033[1;{color_code};40m[{level}]{caller_info}\033[0;0m {message}"
        self.lines.append(text)
        self.curent_line += 1
        print(text)
        return Line(timestamp, color_code, level, caller_info, content,self.curent_line, self)
        
    def info(self, *content: Any):
        self.log('INFO', '32', *content)

    def warn(self, *content: Any):
        self.log('WARN', '33', *content)

    def crit(self, *content: Any):
        self.log('CRIT', '31', *content)

    def debug(self, *content: Any):
        self.log('DEBUG', '95', *content)

    def get(self, *content: Any):
        return self.log('GET', '38;5;30', *content)  # Couleur 30

    def post(self, *content: Any):
        return self.log('POST', '38;5;202',  *content)  # Couleur 202