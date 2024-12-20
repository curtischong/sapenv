from all_types_and_consts import Species
from pet_data import get_base_pet
from shop import Shop
from team import Team


class Player:
    def __init__(self, team: Team):
        self.team = team
        self.shop = Shop()

    @staticmethod
    def init_starting_player():
        player = Player(Team.init_starting_team())
        player.shop.init_shop_for_round()
        return player

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

    # TODO: do we allow combining pets if the target pet is already at max level?
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
