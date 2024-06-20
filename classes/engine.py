from datetime import datetime
from typing import Literal
from random import choice, Random, choices

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

class RangeSettings:
    def __init__(self, add_range: list[int], subtract_range: list[int], divide_range: list[int], multiply_range: list[int]) -> None:
        self.add_range = add_range
        self.subtract_range = subtract_range
        self.divide_range = divide_range
        self.multiply_range = multiply_range
    
    def __repr__(self) -> str:
        return f"<RangeSettings add_range={self.add_range}, substract_range={self.subtract_range}, divide_range={self.divide_range}, multiply_range={self.multiply_range}"

class Engine:
    def __init__(self, operations: list[Literal['+', '-', '/', '*']] = ['+', '-', '/', '*'], operations_probs: list[float] = [0.25, 0.25, 0.25, 0.25], range: RangeSettings = RangeSettings([1, 10], [1, 10], [1, 10], [1, 10]), length: int = 10, thread_id: str | int = 1, seed: int = None) -> None:
        if seed is None:
            seed = int(datetime.now().timestamp() * 1000)

        self.operations = operations
        self.operations_probs = operations_probs
        self.range = range
        self.length = length
        self.id = thread_id
        self.seed = seed
        self.random = Random(seed)
        self.calcs: list[Calc] = []
        self.generate()
    
    def generate(self):
        for i in range(self.length):
            operation = choices(self.operations, self.operations_probs)[0]
            match operation:
                case '/':
                    while True:
                        x = self.random.randint(self.range.divide_range[0], self.range.divide_range[1])
                        y = self.random.randint(self.range.divide_range[0], self.range.divide_range[1])
                        if x%y == 0:
                            break
                
                case '*':
                    x = self.random.randint(self.range.multiply_range[0], self.range.multiply_range[1])
                    y = self.random.randint(self.range.multiply_range[0], self.range.multiply_range[1])
                
                case '+':
                    x = self.random.randint(self.range.add_range[0], self.range.add_range[1])
                    y = self.random.randint(self.range.add_range[0], self.range.add_range[1])
                
                case '-':
                    x = self.random.randint(self.range.subtract_range[0], self.range.subtract_range[1])
                    y = self.random.randint(self.range.subtract_range[0], self.range.subtract_range[1])
            
            self.calcs.append(Calc(x, y, operation))
    
    def __repr__(self) -> str:
        return f"<Engine length={self.length}, operations={self.operations}, operations_probs={self.operations_probs}, range{self.range}"