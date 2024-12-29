from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Literal
from enum import Enum, auto

IS_TRIGGERS_ENABLED = False

MAX_TEAM_SIZE = 5

# set min attack and min health to 0 because that will be the value for the NONE pet
MIN_ATTACK = 0
MAX_ATTACK = 50


MIN_HEALTH = 0
MAX_HEALTH = 50


PetExperience = Literal[1, 2, 3, 4, 5, 6]
MAX_PET_EXPERIENCE = 6
MIN_PET_EXPERIENCE = 1

MIN_PET_LEVEL = 1
MAX_PET_LEVEL = 3


ShopTier = Literal[1, 2, 3, 4, 5, 6]
MAX_SHOP_TIER = 6


MAX_SHOP_SLOTS = 7  # you can have at most 7 NORMAL shop indexes (5 from normal - 2 more if you freeze linked indexes)
MAX_SHOP_LINKED_SLOTS = MAX_TEAM_SIZE  # since you can promote as most this many pets (by dragging from the shop to them)

# I think MAX_SHOP_FOOD_SLOTS is 18 because the max foods is 3. however, you can sell 5 pigeons to get 3*5 foods. so the shop can have up to 18 food slots. However, I'll make this number 23 just in case
MAX_SHOP_FOOD_SLOTS = 23  # I think having a pigeon and then selling it at a higher tier will allow you to overflow the existing 2 food slots (so you can have an extra food). Cow CLEARs the shop. so there's no risk of overflowing
STARTING_GOLD = 10
MAX_GOLD = 30
PET_COST = 3
FOOD_COST = 3
ROLL_COST = 1

STARTING_HEARTS = 5
TURN_AT_WHICH_THEY_GAIN_ONE_LOST_HEART = 3


# RL constants:
MAX_ACTIONS_IN_TURN = 20


def dummy_trigger_fn(**kwargs):
    pass


class Species(Enum):
    NONE = auto()

    # tier 1
    DUCK = auto()
    BEAVER = auto()
    PIGEON = auto()
    OTTER = auto()
    PIG = auto()
    ANT = auto()
    MOSQUITO = auto()
    FISH = auto()
    CRICKET = auto()
    HORSE = auto()

    # tier 2
    SNAIL = auto()
    CRAB = auto()
    SWAN = auto()
    RAT = auto()
    HEDGEHOG = auto()
    PEACOCK = auto()
    FLAMINGO = auto()
    WORM = auto()
    KANGAROO = auto()
    SPIDER = auto()

    # tier 3
    DODO = auto()
    BADGER = auto()
    DOLPHIN = auto()
    GIRAFFE = auto()
    ELEPHANT = auto()
    CAMEL = auto()
    RABBIT = auto()
    OX = auto()
    DOG = auto()
    SHEEP = auto()

    # tier 4
    SKUNK = auto()
    HIPPO = auto()
    BISON = auto()
    BLOWFISH = auto()
    TURTLE = auto()
    SQUIRREL = auto()
    PENGUIN = auto()
    DEER = auto()
    WHALE = auto()
    PARROT = auto()

    # tier 5
    SCORPION = auto()
    CROCODILE = auto()
    RHINO = auto()
    MONKEY = auto()
    ARMADILLO = auto()
    COW = auto()
    SEAL = auto()
    ROOSTER = auto()
    SHARK = auto()
    TURKEY = auto()

    # tier 6
    LEOPARD = auto()
    BOAR = auto()
    TIGER = auto()
    WOLVERINE = auto()
    GORILLA = auto()
    DRAGON = auto()
    MAMMOTH = auto()
    CAT = auto()
    SNAKE = auto()
    FLY = auto()

    # hidden species
    BEE = auto()
    CRICKET_SPAWN = auto()  # spawned when a cricket is killed
    RAT_SPAWN = auto()  # spawned when a rat is killed
    RAM = auto()  # spawned when a sheep is killed
    BUS = auto()
    FLY_SPAWN = auto()  # spawned when a pet is killed


hidden_species = [
    Species.BEE,
    Species.CRICKET_SPAWN,
    Species.RAT_SPAWN,
    Species.RAM,
    Species.BUS,
    Species.FLY_SPAWN,
]


class Food(Enum):
    # tier 1
    APPLE = auto()
    HONEY = auto()

    # tier 2
    PILL = auto()
    MEAT_BONE = auto()
    CUPCAKE = auto()

    # tier 3
    SALAD_BOWL = auto()
    GARLIC = auto()

    # tier 4
    CANNED_FOOD = auto()
    PEAR = auto()

    # tier 5
    CHILI = auto()
    CHOCOLATE = auto()
    SUSHI = auto()

    # tier 6
    STEAK = auto()
    MELON = auto()
    MUSHROOM = auto()
    PIZZA = auto()

    # hidden foods
    MILK = auto()
    BREAD_CRUMB = auto()  # from pigeon (can overflow the food slots)


hidden_foods = [
    Food.MILK,
    Food.BREAD_CRUMB,
]

food_tiers = {
    1: [Food.APPLE, Food.HONEY],
    2: [Food.PILL, Food.MEAT_BONE, Food.CUPCAKE],
    3: [Food.SALAD_BOWL, Food.GARLIC],
    4: [Food.CANNED_FOOD, Food.PEAR],
    5: [Food.CHILI, Food.CHOCOLATE, Food.SUSHI],
    6: [Food.STEAK, Food.MELON, Food.MUSHROOM, Food.PIZZA],
}

avail_food_in_tier = defaultdict(list)
for tier in range(1, 7):
    avail_food_in_tier[tier] = avail_food_in_tier[tier - 1] + food_tiers[tier]

foods_that_apply_globally = [Food.SALAD_BOWL, Food.CANNED_FOOD, Food.SUSHI, Food.PIZZA]
foods_for_pet = [
    Food.APPLE,
    Food.HONEY,
    Food.PILL,
    Food.MEAT_BONE,
    Food.CUPCAKE,
    Food.GARLIC,
    Food.PEAR,
    Food.CHILI,
    Food.CHOCOLATE,
    Food.STEAK,
    Food.MELON,
    Food.MUSHROOM,
    # hidden ones:
    Food.MILK,
    Food.BREAD_CRUMB,
]
assert len(foods_that_apply_globally) + len(foods_for_pet) == len(Food)


class BattleResult(Enum):
    WON_BATTLE = auto()
    LOST_BATTLE = auto()
    TIE = auto()


NUM_WINS_TO_WIN = 10
MAX_GAMES_LENGTH = 30  # if they play more than these number of turns, they lose automatically (to prevent infinite episodes)


class GameResult(Enum):
    CONTINUE = auto()
    WIN = auto()
    LOSE = auto()
    TRUNCATED = auto()


@dataclass
class SelectedAction:
    path_key: str
    params: tuple[int, ...]


class ActionReturn(Enum):
    GAME_RESULT = auto()  # Did the player win/lose/continue the game?
    BATTLE_RESULT = auto()  # did the player lose or win the battle it just fought?
    BOUGHT_PET_SPECIES = auto()
    SOLD_PET_SPECIES = auto()


ActionResult = dict[ActionReturn, Any]


class Effect(Enum):
    NONE = auto()
    BEE = auto()
    MEAT_BONE = auto()
    GARLIC = auto()
    CHILLI = auto()
    STEAK = auto()
    MELON = auto()
    MUSHROOM = auto()
    PEANUT = auto()
