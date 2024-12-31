from collections import defaultdict
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
            res.append(pet.apply_temp_buffs())
        return res

    def get_non_none_pets(self) -> list[Pet]:
        return [pet for pet in self.pets if pet.species != Species.NONE]

    # Note: this function ensures that the returned pets are not NONE
    def get_random_pets(
        self, select_num_pets: int, exclude_pet: Pet | None = None
    ) -> list[Pet]:
        return Team.get_random_pets_from_list(self.pets, select_num_pets, exclude_pet)

    @staticmethod
    # Note: this function ensures that the returned pets are not NONE
    def get_random_pets_from_list(
        pets_list: list[Pet], select_num_pets: int, exclude_pet: Pet | None = None
    ) -> list[Pet]:
        pets_without_none: list[Pet] = []
        for pet in pets_list:
            is_not_excluded_pet = exclude_pet is None or pet is not exclude_pet
            if pet.species != Species.NONE and is_not_excluded_pet:
                pets_without_none.append(pet)

        n = len(pets_without_none)
        return random.sample(pets_without_none, min(n, select_num_pets))

    def get_pets(self, species_to_list_first: list[Species] = []) -> list[Pet]:
        # we cannot just pop the indexes one by one. I tried in jupyter:
        # l=[1,2,3,4,5,6]
        # for a in l:
        #     print(l.pop(l.index(a)))

        # first create a mapping of species -> pets of that species
        species_to_pets = defaultdict(list)
        for pet in self.pets:
            species_to_pets[pet.species].append(pet)

        res = []

        for species in species_to_list_first:
            res += species_to_pets[species]

        for pet in self.pets:
            if pet not in res:
                res.append(pet)
        return res
