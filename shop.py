import itertools
from all_types_and_consts import ShopTier, Species, hidden_species
from pet import Pet
import random
from pet_data import shop_tier_to_pets_map

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
    if species1.value < species2.value:
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


class ShopSlot:
    def __init__(self, pet: Pet):
        self.pet = pet
        self.is_frozen: bool = False


class LinkedShopSlot:
    def __init__(self, pet1: Pet, pet2: Pet):
        self.pet1 = pet1
        self.pet2 = pet2


class Shop:
    def __init__(self):
        self.shop_tier: ShopTier = 1
        self.slots: list[ShopSlot] = []
        self.linked_slots: list[LinkedShopSlot] = []

    def init_shop_for_round(self, round_number: int):
        # similar to roll_shop but there are higher chances for pets of the current tier
        if round_number in ROUND_TO_SHOP_TIER:
            self.shop_tier = ROUND_TO_SHOP_TIER[round_number]
        self.roll_shop()

    # I'm pretty sure that each animal has an EQUAL chance to be rolled. There is no special weighting for each species.
    # the only time where the chances are different is when you get a linked slot. in which case it'll always show the shop tier + 1 (or max tier)
    def roll_shop(self):
        # 1) cary over all the frozen slots

        # all linked slots disappear after the shop is rolled
        # In my implementation, if you freeze a linked shop slot, it's no longer a linked shop slot. you chose the species you care about.
        # so you KNOW that there are no no frozen linked shop slots
        self.linked_slots = []

        new_slots = []
        for slot in self.slots:
            if slot.is_frozen:
                new_slots.append(slot)

        # for the free slots left, we generate them
        # I tested in the game. If you freeze all the pets AND the linked slot, and you roll. the frozen pet (from the linked slot) will remain. You basically artificially increase your slots
        num_free_slots = max(
            SHOP_TIER_TO_MAX_SHOP_SLOTS[self.shop_tier] - len(new_slots), 0
        )

        num_pets_available = self.shop_tier * 10
        for _ in range(num_free_slots):
            chosen_species = random.randrange(0, num_pets_available)
            chosen_species_tier = (chosen_species // 10) + 1
            chosen_species_idx_in_tier = chosen_species % 10
            base_pet = shop_tier_to_pets_map[chosen_species_tier][
                chosen_species_idx_in_tier
            ]
            new_slots.append(ShopSlot(base_pet))

        self.slots = new_slots

    # def get_linked_slot_state(self):
    #     species1 = [linked_slot.pet1.species for linked_slot in self.linked_slots]
    #     species2 = [linked_slot.pet2.species for linked_slot in self.linked_slots]
    #     attack = [slot.pet.attack for slot in self.slots]
    #     health = [slot.pet.health for slot in self.slots]
    #     is_frozen = [slot.is_frozen for slot in self.slots]

    #     return {
    #         "species1": species1,
    #         "species2": species2,
    #         "attacks": attack,
    #         "healths": health,
    #         "is_frozen": is_frozen,
    #     }
