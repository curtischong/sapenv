from typing import Literal
from enum import Enum, auto

ShopTier = Literal[1, 2, 3, 4, 5, 6]
PetLevel = Literal[1, 2, 3]
PetExperience = Literal[1, 2, 3]


class Species(Enum):
    DUCK = auto()
    BEAVER = auto()
    PIGEON = auto()
