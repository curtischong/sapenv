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
MAX_SHOP_SLOTS = 7  # you can have at most 7 NORMAL shop indexes (5 from normal - 2 more if you freeze linked indexes)
MAX_SHOP_LINKED_SLOTS = MAX_TEAM_SIZE  # since you can promote as most this many pets (by dragging from the shop to them)

MAX_SHOP_FOOD_SLOTS = 3  # I think having a pigeon and then selling it at a higher tier will allow you to overflow the existing 2 food slots (so you can have an extra food). Cow CLEARs the shop. so there's no risk of overflowing


class Species(Enum):
    NONE = auto()
    DUCK = auto()
    BEAVER = auto()
    PIGEON = auto()

    # hidden species
    RAM = auto()
    BUS = auto()


hidden_species = [
    Species.RAM,
    Species.BUS,
]


class Foods(Enum):
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
    # PEANUT = auto()
    BREAD_CRUMB = auto()  # from pigeon (can overflow the food slots)


hidden_foods = [
    Foods.MILK,
    # Foods.PEANUT,
    Foods.BREAD_CRUMB,
]


# buyable_foods = []
# for food in Foods:
#     if food is Foods.NONE or food is Foods.PEANUT:
#         continue
#     buyable_foods.append(food)

food_tiers = {
    1: [Foods.APPLE, Foods.HONEY],
    2: [Foods.PILL, Foods.MEAT_BONE, Foods.CUPCAKE],
    3: [Foods.SALAD_BOWL, Foods.GARLIC],
    4: [Foods.CANNED_FOOD, Foods.PEAR],
    5: [Foods.CHILI, Foods.CHOCOLATE, Foods.SUSHI],
    6: [Foods.STEAK, Foods.MELON, Foods.MUSHROOM, Foods.PIZZA],
}
