from typing import Literal
from enum import Enum, auto

MAX_TEAM_SIZE = 5

MIN_ATTACK = 1
MAX_ATTACK = 50


MIN_HEALTH = 1
MAX_HEALTH = 50

ShopTier = Literal[1, 2, 3, 4, 5, 6]

# I could've made the experience and level the same. but 1) it's easier to read it this way. and 2) it's simpler for the model to read the "level" of a pet

PetLevel = Literal[1, 2, 3]
MAX_PET_LEVEL = 3
MIN_PET_LEVEL = 1

PetExperience = Literal[1, 2, 3]
MAX_PET_EXPERIENCE = 3
MIN_PET_EXPERIENCE = 1


class Species(Enum):
    DUCK = auto()
    BEAVER = auto()
    PIGEON = auto()
