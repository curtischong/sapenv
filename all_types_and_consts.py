from typing import Literal
from enum import Enum, auto

MAX_TEAM_SIZE = 5

MIN_ATTACK = 1
MAX_ATTACK = 50


MIN_HEALTH = 1
MAX_HEALTH = 50


# I could've made the experience and level the same. but 1) it's easier to read it this way. and 2) it's simpler for the model to read the "level" of a pet

PetLevel = Literal[1, 2, 3]
MAX_PET_LEVEL = 3
MIN_PET_LEVEL = 1

PetExperience = Literal[1, 2, 3]
MAX_PET_EXPERIENCE = 2  # since when we hit experience 3, we are sent to level 3 and cannot collect more experience
MIN_PET_EXPERIENCE = 0


ShopTier = Literal[1, 2, 3, 4, 5, 6]
MAX_SHOP_SLOTS = 6
MAX_SHOP_LINKED_SLOTS = MAX_TEAM_SIZE  # since you can promote as most this many pets
MAX_TOTAL_SHOP_SLOTS = MAX_SHOP_LINKED_SLOTS + MAX_SHOP_SLOTS

MAX_SHOP_FOOD_SLOTS = 3


class Species(Enum):
    NONE = auto()
    DUCK = auto()
    BEAVER = auto()
    PIGEON = auto()

    # hidden species
    RAM = auto()
    BUS = auto()


class FoodKind(Enum):
    NONE = auto()
    APPLE = auto()
    HONEY = auto()
    PILL = auto()
    MEAT_BONE = auto()
    CUPCAKE = auto()
    SALAD_BOWL = auto()
    GARLIC = auto()
    CANNED_FOOD = auto()
    PEAR = auto()
    CHILI = auto()
    CHOCOLATE = auto()
    SUSHI = auto()
    STEAK = auto()
    MELON = auto()
    MUSHROOM = auto()
    PIZZA = auto()

    # hidden foods
    MILK = auto()
    PEANUT = auto()
