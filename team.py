from all_types_and_consts import MAX_TEAM_SIZE, Species
from pet import Pet
from pet_data import get_base_pet
import numpy as np
import random


class Team:
    def __init__(self, pets: list[Pet]):
        self.pets = pets
        assert len(pets) == MAX_TEAM_SIZE

    @staticmethod
    def init_starting_team():
        return Team(pets=[get_base_pet(Species.NONE) for _ in range(MAX_TEAM_SIZE)])

    def get_observation(self):
        num_pets = len(self.pets)
        experiences = np.zeros((num_pets,), dtype=np.int32)

        # TODO: do effects as well
        for idx, pet in enumerate(self.pets):
            experiences[idx] = pet.experience

        return Pet.get_base_stats_observation(self.pets) | {"experiences": experiences}

    def __eq__(self, other: "Team"):
        return self.pets == other.pets

    def clone(self):
        return Team([pet.clone() for pet in self.pets])

    def get_pets_for_battle(self) -> list[Pet]:
        res = []
        for pet in self.pets:
            if pet.species == Species.NONE:
                continue
            res.append(pet.add_stats(attack=pet.attack_boost, health=pet.health_boost))
        return res

    # Note: this function ensures that the returned pets are not NONE
    def get_random_pets(self, select_num_pets: int) -> list[Pet]:
        pets_with_indexes = Team.get_random_pets_with_idxs(self.pets, select_num_pets)
        return [pet for pet, idx in pets_with_indexes]

    @staticmethod
    # returns a list of (pet, idx_in_team)
    # Note: this function ensures that the returned pets are not NONE
    def get_random_pets_with_idxs(
        pets_list: list[Pet], select_num_pets: int
    ) -> list[tuple[Pet, int]]:
        pets_without_none: list[tuple[Pet, int]] = []  # list of (pet, idx_in_team)
        for idx, pet in enumerate(pets_list):
            if pet.species != Species.NONE:
                pets_without_none.append((pet, idx))
        selected_indexes = random.sample(range(len(pets_without_none)), select_num_pets)

        res = []
        for idx in selected_indexes:
            res.append(pets_without_none[idx])
        return res
