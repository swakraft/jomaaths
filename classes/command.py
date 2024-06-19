from enum import Enum

class Command(Enum):

    speedmath_start = "</speedmath start:1252681571354542134>"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return self.value