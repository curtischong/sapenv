from collections import defaultdict
import itertools
from all_types_and_consts import (
    FOOD_COST,
    MAX_SHOP_LINKED_SLOTS,
    MAX_SHOP_SLOTS,
    PET_COST,
    ROLL_COST,
    STARTING_GOLD,
    Food,
    ShopTier,
    Species,
    hidden_species,
    avail_food_in_tier,
    foods_that_apply_globally,
    foods_for_pet,
)
from pet import Pet
import random
from pet_data import get_base_pet, shop_tier_to_pets_map
import numpy as np

from utils import extend_array_to_length, extend_pet_array_to_length

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

SHOP_TIER_TO_MAX_FOOD_SLOTS: dict[ShopTier, int] = {
    1: 2,
    2: 2,
    3: 2,
    4: 3,
    5: 3,
    6: 3,
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

    def __repr__(self):
        if self.is_frozen:
            return f"🧊{self.pet}🧊"
        return str(self.pet)


class LinkedShopSlot:
    def __init__(self, pet1: Pet, pet2: Pet):
        self.pet1 = pet1
        self.pet2 = pet2

    def __repr__(self):
        return f"{self.pet1}|--|{self.pet2})"


class Shop:
    def __init__(self):
        self.shop_tier: ShopTier = 1
        self.slots: list[ShopSlot] = []
        self.linked_slots: list[LinkedShopSlot] = []
        self.gold: int = STARTING_GOLD
        self.num_foods: defaultdict[Food, int] = defaultdict(int)
        self.num_frozen_foods: defaultdict[Food, int] = defaultdict(int)

    def init_shop_for_round(self, round_number: int):
        # TODO: add additional gold from swans. we should call pet callbacks to do this? maybe there is no logic required here
        self.gold = (
            STARTING_GOLD + 1
        )  # add 1 gold since when we roll_shop we lose 1 gold

        if round_number in ROUND_TO_SHOP_TIER:
            self.shop_tier = ROUND_TO_SHOP_TIER[round_number]
        self.roll_shop()

    # I'm pretty sure that each animal has an EQUAL chance to be rolled. There is no special weighting for each species.
    # the only time where the chances are different is when you get a linked slot. in which case it'll always show the shop tier + 1 (or max tier)
    def roll_shop(self):
        assert self.gold >= ROLL_COST
        self.gold -= ROLL_COST

        # 1) carry over all the frozen slots

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

        # multiply by 10 since right now, in the game, there are 10 pets per tier
        num_pets_available = self.shop_tier * 10
        for _ in range(num_free_slots):
            chosen_species = random.randrange(0, num_pets_available)
            chosen_species_tier = (chosen_species // 10) + 1
            chosen_species_idx_in_tier = chosen_species % 10
            base_pet = shop_tier_to_pets_map[chosen_species_tier][
                chosen_species_idx_in_tier
            ].clone()  # we need to clone the pet so we don't modify the original
            new_slots.append(ShopSlot(base_pet))

        self.slots = new_slots

        # now handle food
        self._roll_food()

    def _roll_food(self):
        self.num_foods.clear()
        # carry over all the frozen foods
        num_frozen_foods = 0
        for food_type, num_frozen in self.num_frozen_foods.items():
            self.num_foods[food_type] = num_frozen
            num_frozen_foods += num_frozen

        available_foods = avail_food_in_tier[self.shop_tier]
        num_food_slots = SHOP_TIER_TO_MAX_FOOD_SLOTS[self.shop_tier]

        num_foods_to_roll = max(0, num_food_slots - num_frozen_foods)
        for _ in range(num_foods_to_roll):
            chosen_food = random.choice(available_foods)
            self.num_foods[chosen_food] += 1

    def freeze_food(self, food_type: Food):
        assert self.num_frozen_foods[food_type] < self.num_foods[food_type]
        self.num_frozen_foods[food_type] += 1

    def unfreeze_food(self, food_type: Food):
        assert self.num_frozen_foods[food_type] > 0
        self.num_frozen_foods[food_type] -= 1

    def toggle_freeze_slot(self, slot_idx: int):
        assert slot_idx < len(self.slots)
        self.slots[slot_idx].is_frozen = not self.slots[slot_idx].is_frozen

    def freeze_pet_at_linked_slot(self, linked_slot_idx: int, is_freezing_pet1: bool):
        assert linked_slot_idx < len(self.linked_slots)
        froze_linked_slot = self.linked_slots.pop(linked_slot_idx)

        if is_freezing_pet1:
            froze_pet = froze_linked_slot.pet1
        else:
            froze_pet = froze_linked_slot.pet2

        # now put this frozen pet into a new slot
        new_slot = ShopSlot(froze_pet)
        new_slot.is_frozen = True
        self.slots.append(new_slot)

    def pet_at_slot(self, idx: int) -> Pet:
        if idx >= len(self.slots):
            return get_base_pet(Species.NONE)
        return self.slots[idx].pet

    def pet_at_linked_slot(self, idx: int, is_quering_for_pet1: bool) -> Pet:
        if idx >= len(self.linked_slots):
            return get_base_pet(Species.NONE)
        linked_slot = self.linked_slots[idx]
        if is_quering_for_pet1:
            return linked_slot.pet1
        else:
            return linked_slot.pet2

    def buy_pet_at_slot(self, slot_idx: int) -> Pet:
        assert self.gold >= PET_COST
        self.gold -= PET_COST
        return self.slots.pop(slot_idx).pet

    def buy_pet_at_linked_slot(self, linked_slot_idx: int, is_pet1_bought: bool) -> Pet:
        assert self.gold >= PET_COST
        self.gold -= PET_COST
        bought_linked_slot = self.linked_slots.pop(linked_slot_idx)
        if is_pet1_bought:
            return bought_linked_slot.pet1
        else:
            return bought_linked_slot.pet2

    def _buy_food_helper(self, food_type: Food):
        cost = self.food_cost(food_type)
        assert self.gold >= cost
        assert self.num_foods[food_type] > 0
        self.num_foods[food_type] -= 1

        # prioritize buying nonfrozen foods
        self.num_frozen_foods[food_type] = min(
            self.num_frozen_foods[food_type], self.num_foods[food_type]
        )
        self.gold -= cost

    def buy_food(self, food_type: Food):
        assert food_type in foods_that_apply_globally
        self._buy_food_helper(food_type)

    def buy_food_for_pet(self, food_type: Food):
        assert food_type in foods_for_pet
        self._buy_food_helper(food_type)

    def food_cost(self, food_type: Food):
        match food_type:
            case Food.PILL:
                return 1
            case Food.BREAD_CRUMB:
                return 0
            case Food.MILK:
                return 0
            case _:
                return FOOD_COST

    def get_observation(self):
        slot_pets_observation = Pet.get_base_stats_observation(
            extend_pet_array_to_length(
                [slot.pet for slot in self.slots], length=MAX_SHOP_SLOTS
            )
        )
        is_slot_pet_frozen = np.array(
            extend_array_to_length(
                [slot.is_frozen for slot in self.slots],
                length=MAX_SHOP_SLOTS,
                get_padded_value=lambda: False,
            ),
            dtype=bool,
        )

        linked_slot_observation1 = Pet.get_base_stats_observation(
            extend_pet_array_to_length(
                [linked_slot.pet1 for linked_slot in self.linked_slots],
                length=MAX_SHOP_LINKED_SLOTS,
            )
        )
        linked_slot_observation2 = Pet.get_base_stats_observation(
            extend_pet_array_to_length(
                [linked_slot.pet2 for linked_slot in self.linked_slots],
                length=MAX_SHOP_LINKED_SLOTS,
            )
        )
        num_foods_observation = np.zeros((len(Food),), dtype=np.int32)
        for food_type, num_foods in self.num_foods.items():
            num_foods_observation[food_type.value] = num_foods

        num_frozen_foods_observation = np.zeros((len(Food),), dtype=np.int32)
        for food_type, num_foods in self.num_frozen_foods.items():
            num_frozen_foods_observation[food_type.value] = num_foods

        return {
            "shop_animals": slot_pets_observation | {"is_frozen": is_slot_pet_frozen},
            "shop_linked_animals": {
                "species1": linked_slot_observation1["species"],
                "species2": linked_slot_observation2["species"],
                "attacks1": linked_slot_observation1["attacks"],
                "attacks2": linked_slot_observation2["attacks"],
                "healths1": linked_slot_observation1["healths"],
                "healths2": linked_slot_observation2["healths"],
            },
            # "shop_num_foods": num_foods_observation,
            # "shop_num_frozen_foods": num_frozen_foods_observation,
        }

    def __repr__(self):
        res = f"{self.gold}💰\n"
        for slot in self.slots:
            res += f" {slot} "
        res += "\n"
        for linked_slot in self.linked_slots:
            res += f" {linked_slot} "
        return res
