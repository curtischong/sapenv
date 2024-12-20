from all_types_and_consts import Species
from pet_data import get_base_pet
from shop import Shop
from team import Team


class Player:
    def __init__(self, team: Team):
        self.team = team
        self.shop = Shop()

    # returns if this reorder is a valid move
    def reorder_team(self, pet_start_idx: int, pet_end_idx: int) -> bool:
        pets = self.team.pets
        if pets[pet_start_idx].species == Species.NONE:
            return False
        if pet_start_idx == pet_end_idx:
            return False

        # Remove the pet from the old position
        pet_to_move = pets.pop(pet_start_idx)

        # Insert it into the new position
        pets.insert(pet_end_idx, pet_to_move)

        return True

    # drag pet 1 to pet 2
    def combine_pets(self, pet1_idx: int, pet2_idx: int) -> bool:
        if pet1_idx == pet2_idx:
            return False  # you cannot combine a pet with itself

        pet1 = self.team.pets[pet1_idx]
        pet2 = self.team.pets[pet2_idx]

        if pet1.species != pet2.species:
            # you cannot combine pets of different species
            return False

        new_pet = pet1.combine_onto(pet2)
        self.team.pets[pet2_idx] = new_pet
        self.team.pets[pet1_idx] = get_base_pet(Species.NONE)

        # PERF: do we delete the old pet?

    def buy_pet_at_slot(self, slot_idx: int, target_team_idx: int) -> bool:
        if self.team.pets[target_team_idx].species != Species.NONE:
            return False

        pet = self.shop.buy_pet_at_slot(slot_idx)
        self.team.pets[target_team_idx] = pet

    def buy_pet_at_linked_slot(
        self, linked_slot_idx: int, is_pet1_bought: bool, target_team_idx: int
    ) -> bool:
        if self.team.pets[linked_slot_idx].species != Species.NONE:
            return False
        pet = self.shop.buy_pet_at_linked_slot(linked_slot_idx, is_pet1_bought)
        self.team.pets[target_team_idx] = pet
