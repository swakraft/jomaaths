from enum import Enum

class Emoji(Enum):



    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return self.value