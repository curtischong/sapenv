from typing import Literal
from enum import Enum, auto

MAX_TEAM_SIZE = 5

MIN_ATTACK = 1
MAX_ATTACK = 50


MIN_HEALTH = 1
MAX_HEALTH = 50


PetExperience = Literal[1, 2, 3, 4, 5, 6]
MAX_PET_EXPERIENCE = 6
MIN_PET_EXPERIENCE = 1

MIN_PET_LEVEL = 1
MAX_PET_LEVEL = 3


ShopTier = Literal[1, 2, 3, 4, 5, 6]


MAX_SHOP_SLOTS = 7  # you can have at most 7 NORMAL shop indexes (5 from normal - 2 more if you freeze linked indexes)
MAX_SHOP_LINKED_SLOTS = MAX_TEAM_SIZE  # since you can promote as most this many pets (by dragging from the shop to them)

MAX_SHOP_FOOD_SLOTS = 3  # I think having a pigeon and then selling it at a higher tier will allow you to overflow the existing 2 food slots (so you can have an extra food). Cow CLEARs the shop. so there's no risk of overflowing
STARTING_GOLD = 10
PET_COST = 3
ROLL_COST = 1

STARTING_HEARTS = 5
TURN_AT_WHICH_THEY_GAIN_ONE_LOST_HEART = 3


def dummy_trigger_fn():
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
    CRICKET_SPAWN = auto()  # spawned when a cricket is killed
    RAM = auto()  # spawned when a sheep is killed
    BUS = auto()
    FLY_SPAWN = auto()  # spawned when a pet is killed


hidden_species = [
    Species.CRICKET_SPAWN,
    Species.RAM,
    Species.BUS,
    Species.FLY_SPAWN,
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


class BattleResult(Enum):
    TEAM1_WIN = auto()
    TEAM2_WIN = auto()
    TIE = auto()


NUM_WINS_TO_WIN = 10
MAX_GAMES_LENGTH = 30  # if they play more than these number of turns, they lose automatically (to prevent infinite episodes)


class GameResult(Enum):
    CONTINUE = auto()
    WIN = auto()
    LOSE = auto()
