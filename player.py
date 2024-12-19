from all_types_and_consts import Species
from team import Team


class Player:
    def __init__(self, team: Team):
        self.team = team

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
