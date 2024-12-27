from all_types_and_consts import MAX_TEAM_SIZE, Species
from pet import Pet
from pet_data import get_base_pet
import numpy as np


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

    def get_pets_without_none_species(self) -> list[Pet]:
        return [pet for pet in self.pets if pet.species != Species.NONE]

    def get_random_pets(self, select_num_pets: int) -> list[Pet]:
        list_copy = self.pets.copy()
        res = []
        while select_num_pets > 0:
            idx = np.random.randint(0, len(list_copy))
            res.append(list_copy.pop(idx))
            select_num_pets -= 1
        return res
