import itertools
from all_types_and_consts import (
    MAX_SHOP_LINKED_SLOTS,
    MAX_TEAM_SIZE,
    PET_COST,
    Species,
    MAX_SHOP_SLOTS,
)
from pet_data import get_base_pet
from shop import Shop
from team import Team
import numpy as np


class Player:
    def __init__(self, team: Team):
        self.team = team
        self.shop = Shop()

    @staticmethod
    def init_starting_player():
        player = Player(Team.init_starting_team())
        player.shop.init_shop_for_round()
        return player

    def reorder_team_action(self, pet_start_idx: int, pet_end_idx: int):
        pets = self.team.pets
        assert pets[pet_start_idx].species != Species.NONE
        assert pet_start_idx != pet_end_idx

        # Remove the pet from the old position
        pet_to_move = pets.pop(pet_start_idx)

        # Insert it into the new position
        pets.insert(pet_end_idx, pet_to_move)

        return True

    def reorder_team_action_mask(self) -> np.ndarray:
        mask = np.ones((MAX_TEAM_SIZE, MAX_TEAM_SIZE), dtype=np.bool)

        # cannot use itertools.combinations since reordering does NOT commute (who is the first pet matters)
        for pet_start_idx in range(MAX_TEAM_SIZE):
            for pet_end_idx in range(MAX_TEAM_SIZE):
                # you cannot move a pet to the same spot
                if pet_start_idx == pet_end_idx:
                    mask[pet_start_idx, pet_end_idx] = False
                    continue

                # you cannot move an empty pet
                pet = self.team.pets[pet_start_idx]
                if pet.species == Species.NONE:
                    mask[pet_start_idx, pet_end_idx] = False
        return mask

    # Note: if a pet is level 3, you cannot combine it AT ALL
    def combine_pets_action(self, pet1_idx: int, pet2_idx: int) -> bool:
        assert pet1_idx != pet2_idx

        pet1 = self.team.pets[pet1_idx]
        pet2 = self.team.pets[pet2_idx]

        assert pet1.species == pet2.species
        assert pet1.species != Species.NONE
        assert pet1.get_level() < 3 and pet2.get_level() < 3

        new_pet = pet1.combine_onto(pet2)
        self.team.pets[pet2_idx] = new_pet
        self.team.pets[pet1_idx] = get_base_pet(Species.NONE)
        # PERF: do we delete the old pet?

    def combine_pets_action_mask(self) -> np.ndarray:
        # the mask is NOT of size n choose 2 since the order of the merged pet matters (dictates who we're merging ONTO).
        mask = np.ones((MAX_TEAM_SIZE, MAX_TEAM_SIZE), dtype=np.bool)

        # we can use itertools since combine_pets validity commutes
        for pet1_idx, pet2_idx in itertools.combinations(range(MAX_TEAM_SIZE), 2):
            # you cannot combine a pet with itself
            if pet1_idx == pet2_idx:
                mask[pet1_idx, pet2_idx] = False
                continue

            # you cannot combine pets of different species
            pet1 = self.team.pets[pet1_idx]
            pet2 = self.team.pets[pet2_idx]
            if pet1.species != pet2.species:
                mask[pet1_idx, pet2_idx] = False
                mask[pet2_idx, pet1_idx] = False
                continue

            # you cannot combine an empty pet
            if pet1.species == Species.NONE:
                mask[pet1_idx, pet2_idx] = False
                mask[pet2_idx, pet1_idx] = False
                continue

            if pet1.get_level() == 3 or pet2.get_level() == 3:
                mask[pet1_idx, pet2_idx] = False
                mask[pet2_idx, pet1_idx] = False
        return mask

    # Note: if a pet is level 3, you cannot buy a pet and combine to the level 3 pet
    def buy_pet_action(self, slot_idx: int, target_team_idx: int) -> bool:
        shop_pet_species = self.shop.pet_at_slot(slot_idx).species
        pet_at_team_idx = self.team.pets[target_team_idx]

        is_player_combining_pets = shop_pet_species == pet_at_team_idx.species
        assert pet_at_team_idx == Species.NONE or is_player_combining_pets

        bought_pet = self.shop.buy_pet_at_slot(slot_idx)
        if is_player_combining_pets:
            self.team.pets[target_team_idx] = bought_pet.combine_onto(pet_at_team_idx)
        else:
            self.team.pets[target_team_idx] = bought_pet

    def buy_pet_action_mask(self) -> np.ndarray:
        # prevent buying if the player does not have enough gold
        if self.shop.gold < PET_COST:
            return np.zeros((MAX_SHOP_SLOTS, MAX_TEAM_SIZE), dtype=np.bool)

        mask = np.ones((MAX_SHOP_SLOTS, MAX_TEAM_SIZE), dtype=np.bool)
        for slot_idx in range(MAX_SHOP_SLOTS):
            # prevent buying a none pet
            shop_pet = self.shop.pet_at_slot(slot_idx)
            if shop_pet.species == Species.NONE:
                mask[slot_idx, :] = False
                continue

            for target_team_idx in range(MAX_TEAM_SIZE):
                target_team_pet = self.team.pets[target_team_idx]

                # you can only buy if you are combining or placing the pet into an empty position
                is_target_position_occupied = target_team_pet != Species.NONE
                is_player_combining_pets = shop_pet.species == target_team_pet.species
                if is_target_position_occupied and not is_player_combining_pets:
                    mask[slot_idx, target_team_idx] = False
        return mask

    def buy_linked_pet_action(
        self, linked_slot_idx: int, is_pet1_bought: bool, target_team_idx: int
    ) -> bool:
        shop_pet_species = self.shop.pet_at_linked_slot(
            linked_slot_idx, is_pet1_bought
        ).species
        pet_at_team_idx = self.team.pets[target_team_idx]

        is_player_combining_pets = shop_pet_species == pet_at_team_idx.species

        assert pet_at_team_idx == Species.NONE or is_player_combining_pets

        bought_pet = self.shop.buy_pet_at_linked_slot(linked_slot_idx, is_pet1_bought)
        if is_player_combining_pets:
            self.team.pets[target_team_idx] = bought_pet.combine_onto(pet_at_team_idx)
        else:
            self.team.pets[target_team_idx] = bought_pet

    def buy_linked_pet_action_mask(self) -> np.ndarray:
        # prevent buying if the player does not have enough gold
        if self.shop.gold < PET_COST:
            return np.zeros((MAX_SHOP_LINKED_SLOTS, 2, MAX_TEAM_SIZE), dtype=np.bool)

        mask = np.ones((MAX_SHOP_SLOTS, 2, MAX_TEAM_SIZE), dtype=np.bool)
        for linked_slot_idx in range(MAX_SHOP_LINKED_SLOTS):
            for buy_pet1 in [True, False]:
                buy_pet_idx = 0 if buy_pet1 else 1

                # prevent buying a none pet
                shop_pet = self.shop.pet_at_linked_slot(linked_slot_idx, buy_pet1)
                if shop_pet.species == Species.NONE:
                    mask[linked_slot_idx, buy_pet_idx, :] = False
                    continue

                for target_team_idx in range(MAX_TEAM_SIZE):
                    target_team_pet = self.team.pets[target_team_idx]

                    # you can only buy if you are combining or placing the pet into an empty position
                    is_target_position_occupied = target_team_pet != Species.NONE
                    is_player_combining_pets = (
                        shop_pet.species == target_team_pet.species
                    )
                    if is_target_position_occupied and not is_player_combining_pets:
                        mask[linked_slot_idx, buy_pet_idx, target_team_idx] = False
        return mask

    def sell_pet_action(self, slot_idx: int):
        pet = self.team.pets[slot_idx]
        assert pet.species != Species.NONE
        self.shop.gold += pet.get_level()

        self.team.pets[slot_idx] = get_base_pet(Species.NONE)

    def sell_pet_action_mask(self) -> np.ndarray:
        mask = np.ones((MAX_TEAM_SIZE), dtype=np.bool)
        for slot_idx in range(MAX_TEAM_SIZE):
            pet = self.team.pets[slot_idx]
            # you cannot sell an empty pet
            if pet.species == Species.NONE:
                mask[slot_idx] = False
        return mask
