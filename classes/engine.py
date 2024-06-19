from typing import Literal
from random import randint as rd, choice

class Calc:
    def __init__(self, x, y, operation) -> None:
        self.x = x
        self.y = y
        self.operation = operation
        self.answer = float(eval(f"{x}{operation}{y}"))
    
    def __repr__(self) -> str:
        return f"<{self.x}{self.operation}{self.y}={self.answer}>"

    def __str__(self) -> str:
        return f"{self.x}{self.operation}{self.y}"

    @property
    def markdown_compatible(self) -> str:
        return self.__str__().replace('*', '\*')

class Engine:
    def __init__(self, operations: list[Literal['+', '-', '/', '*']] = ['+', '-', '/', '*'], range: list[int] = [1, 10], lenght: int = 10, thread_id: str | int = 1) -> None:
        self.operations = operations
        self.min_int = range[0]
        self.max_int = range[1]
        self.lenght = lenght
        self.id = thread_id
        self.calcs: list[Calc] = []
        self.generate()
    
    def generate(self):
        for i in range(self.lenght):
            operation = choice(self.operations)
            if operation == "/":
                while True:
                    x = rd(self.min_int, self.max_int)
                    y = rd(self.min_int, self.max_int)
                    if x%y == 0:
                        break
            
            else:
                x = rd(self.min_int, self.max_int)
                y = rd(self.min_int, self.max_int)

            self.calcs.append(Calc(x, y, operation))