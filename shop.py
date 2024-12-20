import itertools
from all_types_and_consts import ShopTier, Species, hidden_species
from pet import Pet

ROUND_TO_SHOP_TIER: dict[int, ShopTier] = {
    1: 1,
    3: 2,
    5: 3,
    7: 4,
    9: 5,
    11: 6,
}

SHOP_TIER_TO_MAX_SHOP_SLOTS: dict[ShopTier, int] = {
    1: 3,
    2: 3,
    3: 4,
    4: 4,
    5: 5,
    6: 5,
}


# since the linked species is independent of the order, this just ensures the tuples are the same each time
def species_to_linked_species(species1: Species, species2: Species):
    if species1 < species2:
        return (species1, species2)
    else:
        return (species2, species1)


def create_linked_species_list():
    buyable_species = []
    for species in Species:
        if species is Species.NONE or species in hidden_species:
            continue
        buyable_species.append(species)

    linked_species_list = []
    num_buyable_species = len(buyable_species)
    for idx1, idx2 in itertools.combinations(range(num_buyable_species), 2):
        species1 = buyable_species[idx1]
        species2 = buyable_species[idx2]

        linked_species_list.append(species_to_linked_species(species1, species2))
    return linked_species_list


linked_species = create_linked_species_list()


class Shop:
    def __init__(self):
        self.shop_tier: ShopTier = 1
        self.slots: list[ShopSlot] = []
        self.linked_slots: list[ShopSlot] = []
        self.is_frozen: list[bool] = []

    def init_shop_for_round(self, round_number: int):
        # similar to roll_shop but there are higher chances for pets of the current tier
        if round_number in ROUND_TO_SHOP_TIER:
            self.shop_tier = ROUND_TO_SHOP_TIER[round_number]
        self.roll_shop()

    # I'm pretty sure that each animal has an EQUAL chance to be rolled. There is no special weighting for each species.
    # the only time where the chances are different is when you get a linked slot. in which case it'll always show the shop tier + 1 (or max tier)
    def roll_shop(self):
        new_slots = []
        for slot in self.linked_slots:
            if slot.is_frozen:
                new_slots.append(slot)
        self.linked_slots = []  # all linked slots disappear after the shop is randomized

        # I tested in the game. If you freeze all the pets AND the linked slot, and you roll. the frozen pet (from the linked slot) will remain

        for slot in self.slots:
            if slot.is_frozen:
                new_slots.append(slot)
            else:
                new_slots.append(ShopSlot())
        self.slots = new_slots

    def freeze_pet(self, ShopSlot):
        self.is_frozen[self.shop_tier] = True


class LinkedShopSlot:
    def __init__(self):
        self.pet: Pet = None
        self.is_frozen: bool = False


class ShopSlot:
    def __init__(self):
        self.pet: Pet = None
        self.is_frozen: bool = False
