import itertools
import math
from all_types_and_consts import MAX_TEAM_SIZE, Species
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

    # TODO: do we allow combining pets if the target pet is already at max level?
    # drag pet 1 to pet 2
    def combine_pets_action(self, pet1_idx: int, pet2_idx: int) -> bool:
        assert pet1_idx != pet2_idx

        pet1 = self.team.pets[pet1_idx]
        pet2 = self.team.pets[pet2_idx]

        assert pet1.species == pet2.species
        assert pet1.species != Species.NONE

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
                mask[pet2_idx, pet1_idx] = (
                    False  # we can make the same relation since we know the species are the same
                )
        return mask

    def buy_pet_at_slot(self, slot_idx: int, target_team_idx: int) -> bool:
        shop_pet_species = self.shop.pet_at_slot(slot_idx).species
        pet_at_team_idx = self.team.pets[target_team_idx]

        is_player_trying_to_combine = shop_pet_species == pet_at_team_idx.species
        if pet_at_team_idx != Species.NONE and not is_player_trying_to_combine:
            # the player is trying to put the bought spot to an incompatible pet. fail
            return False

        bought_pet = self.shop.buy_pet_at_slot(slot_idx)
        if is_player_trying_to_combine:
            self.team.pets[target_team_idx] = bought_pet.combine_onto(pet_at_team_idx)
        else:
            self.team.pets[target_team_idx] = bought_pet

    def buy_pet_at_linked_slot(
        self, linked_slot_idx: int, is_pet1_bought: bool, target_team_idx: int
    ) -> bool:
        shop_pet_species = self.shop.pet_at_linked_slot(
            linked_slot_idx, is_pet1_bought
        ).species
        pet_at_team_idx = self.team.pets[target_team_idx]

        is_player_trying_to_combine = shop_pet_species == pet_at_team_idx.species

        if pet_at_team_idx != Species.NONE and not is_player_trying_to_combine:
            # the player is trying to put the bought spot to an incompatible pet. fail
            return False

        bought_pet = self.shop.buy_pet_at_linked_slot(linked_slot_idx, is_pet1_bought)
        if is_player_trying_to_combine:
            self.team.pets[target_team_idx] = bought_pet.combine_onto(pet_at_team_idx)
        else:
            self.team.pets[target_team_idx] = bought_pet

    def sell_pet_at_slot(self, slot_idx: int):
        pet = self.team.pets[slot_idx]
        assert pet.species != Species.NONE
        self.shop.gold += pet.get_level()

        self.team.pets[slot_idx] = get_base_pet(Species.NONE)
