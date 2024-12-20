from all_types_and_consts import MAX_TEAM_SIZE, Species
from pet import Pet


class Team:
    def __init__(self, pets: list[Pet]):
        self.pets = pets
        assert len(pets) == MAX_TEAM_SIZE

    def __eq__(self, other: "Team"):
        return self.pets == other.pets

    def clone(self):
        return Team([pet.clone() for pet in self.pets])

    def get_pets_without_none_species(self) -> list[Pet]:
        return [pet for pet in self.pets if pet.species != Species.NONE]
