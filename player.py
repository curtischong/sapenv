import itertools
import math
from all_types_and_consts import (
    MAX_GAMES_LENGTH,
    MAX_SHOP_LINKED_SLOTS,
    MAX_TEAM_SIZE,
    NUM_WINS_TO_WIN,
    PET_COST,
    ROLL_COST,
    STARTING_HEARTS,
    TURN_AT_WHICH_THEY_GAIN_ONE_LOST_HEART,
    BattleResult,
    GameResult,
    Species,
    MAX_SHOP_SLOTS,
)
from battle import battle
from environment.action_space import ActionName
from gen_opponent import get_horse_team, get_pig_team
from pet_data import get_base_pet
from shop import Shop
from team import Team
import numpy as np

from utils import apply_permutation


class Player:
    def __init__(self, team: Team):
        self.team = team
        self.shop = Shop()
        self.turn_number = 0
        self.num_wins = 0
        self.num_actions_taken_in_turn = 0
        self.hearts = STARTING_HEARTS

        self.permutations: list[list[int]] = [
            p for p in itertools.permutations(list(range(MAX_TEAM_SIZE)))
        ]
        self.last_action_name: ActionName | None = None

    @staticmethod
    def init_starting_player():
        player = Player(Team.init_starting_team())
        player.shop.init_shop_for_round(round_number=1)
        return player

    def reorder_team_action(self, reorder_type: int):
        pets = self.team.pets
        assert reorder_type < len(self.permutations)
        reorders = self.permutations[reorder_type]
        for old_idx, new_idx in enumerate(reorders):
            if new_idx != old_idx:
                # ensure that the species that we're reordering is not NONE
                assert pets[old_idx].species != Species.NONE

        self.team.pets = apply_permutation(pets, reorders)

    def reorder_team_action_mask(self) -> np.ndarray:
        if self.last_action_name == ActionName.REORDER_TEAM:
            # disable reordering if the last action was reorder
            return np.zeros((math.factorial(MAX_TEAM_SIZE)), dtype=bool)

        mask = np.ones((math.factorial(MAX_TEAM_SIZE)), dtype=bool)

        for i, reorders in enumerate(self.permutations):
            for old_idx, new_idx in enumerate(reorders):
                pet = self.team.pets[old_idx]
                if old_idx != new_idx and pet.species == Species.NONE:
                    mask[i] = False
                    break

        mask[0] = False  # you cannot reorder into the same order
        return mask

    # Note: if a pet is level 3, you cannot combine it AT ALL
    def combine_pets_action(self, pet1_idx: int, pet2_idx: int):
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
        mask = np.ones((MAX_TEAM_SIZE, MAX_TEAM_SIZE), dtype=bool)

        for i in range(MAX_TEAM_SIZE):
            # this must be done outside the itertools.combinations loop since this index is outside the cases for n choose 2
            # you cannot combine a pet with itself
            mask[i, i] = False

        # we can use itertools since combine_pets validity commutes
        for pet1_idx, pet2_idx in itertools.combinations(range(MAX_TEAM_SIZE), 2):
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
    def buy_pet_action(self, slot_idx: int, target_team_idx: int):
        shop_pet_species = self.shop.pet_at_slot(slot_idx).species
        pet_at_team_idx = self.team.pets[target_team_idx]

        is_player_combining_pets = shop_pet_species == pet_at_team_idx.species
        assert pet_at_team_idx.species == Species.NONE or is_player_combining_pets

        bought_pet = self.shop.buy_pet_at_slot(slot_idx)
        if is_player_combining_pets:
            self.team.pets[target_team_idx] = bought_pet.combine_onto(pet_at_team_idx)
        else:
            self.team.pets[target_team_idx] = bought_pet

    def buy_pet_action_mask(self) -> np.ndarray:
        # prevent buying if the player does not have enough gold
        if self.shop.gold < PET_COST:
            return np.zeros((MAX_SHOP_SLOTS, MAX_TEAM_SIZE), dtype=bool)

        mask = np.ones((MAX_SHOP_SLOTS, MAX_TEAM_SIZE), dtype=bool)
        for slot_idx in range(MAX_SHOP_SLOTS):
            # prevent buying a none pet
            shop_pet = self.shop.pet_at_slot(slot_idx)
            if shop_pet.species == Species.NONE:
                mask[slot_idx, :] = False
                continue

            for target_team_idx in range(MAX_TEAM_SIZE):
                target_team_pet = self.team.pets[target_team_idx]

                # you can only buy if you are combining or placing the pet into an empty position
                is_target_position_occupied = target_team_pet.species != Species.NONE
                is_player_combining_pets = shop_pet.species == target_team_pet.species
                if is_target_position_occupied and not is_player_combining_pets:
                    mask[slot_idx, target_team_idx] = False
        return mask

    def buy_linked_pet_action(
        self, linked_slot_idx: int, is_pet1_bought: bool, target_team_idx: int
    ):
        shop_pet_species = self.shop.pet_at_linked_slot(
            linked_slot_idx, is_pet1_bought
        ).species
        pet_at_team_idx = self.team.pets[target_team_idx]

        is_player_combining_pets = shop_pet_species == pet_at_team_idx.species

        assert pet_at_team_idx.species == Species.NONE or is_player_combining_pets

        bought_pet = self.shop.buy_pet_at_linked_slot(linked_slot_idx, is_pet1_bought)
        if is_player_combining_pets:
            self.team.pets[target_team_idx] = bought_pet.combine_onto(pet_at_team_idx)
        else:
            self.team.pets[target_team_idx] = bought_pet

    def buy_linked_pet_action_mask(self) -> np.ndarray:
        # prevent buying if the player does not have enough gold
        if self.shop.gold < PET_COST:
            return np.zeros((MAX_SHOP_LINKED_SLOTS, 2, MAX_TEAM_SIZE), dtype=bool)

        mask = np.ones((MAX_SHOP_LINKED_SLOTS, 2, MAX_TEAM_SIZE), dtype=bool)
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
                    is_target_position_occupied = (
                        target_team_pet.species != Species.NONE
                    )
                    is_player_combining_pets = (
                        shop_pet.species == target_team_pet.species
                    )
                    if is_target_position_occupied and not is_player_combining_pets:
                        mask[linked_slot_idx, buy_pet_idx, target_team_idx] = False
        return mask

    def sell_pet_action(self, idx: int):
        pet = self.team.pets[idx]
        assert pet.species != Species.NONE
        self.shop.gold += pet.get_level()

        self.team.pets[idx] = get_base_pet(Species.NONE)

    def sell_pet_action_mask(self) -> np.ndarray:
        mask = np.ones((MAX_TEAM_SIZE), dtype=bool)
        for slot_idx in range(MAX_TEAM_SIZE):
            pet = self.team.pets[slot_idx]
            # you cannot sell an empty pet
            if pet.species == Species.NONE:
                mask[slot_idx] = False
        return mask

    def roll_shop_action(self):
        self.shop.roll_shop()

    def roll_shop_action_mask(self) -> np.ndarray:
        if self.shop.gold < ROLL_COST:
            return np.zeros((1), dtype=bool)
        else:
            return np.ones((1), dtype=bool)

    def toggle_freeze_slot_action(self, slot_idx: int):
        self.shop.toggle_freeze_slot(slot_idx)

    def toggle_freeze_slot_action_mask(self) -> np.ndarray:
        # return np.zeros( (MAX_SHOP_SLOTS), dtype=bool)  # comment this out to disable toggle freeze slot
        mask = np.zeros((MAX_SHOP_SLOTS), dtype=bool)

        # ensure the slots we freeze/unfreeze are available
        for slot_idx in range(len(self.shop.slots)):
            mask[slot_idx] = True
        return mask

    def freeze_pet_at_linked_slot_action(self, slot_idx: int, is_freezing_pet1: bool):
        self.shop.freeze_pet_at_linked_slot(slot_idx, is_freezing_pet1)

    def freeze_pet_at_linked_slot_action_mask(self) -> np.ndarray:
        mask = np.zeros((MAX_SHOP_LINKED_SLOTS), dtype=bool)
        for slot_idx in range(len(self.shop.linked_slots)):
            mask[slot_idx] = True
        return mask

    def end_turn_action(self) -> GameResult:
        # todo: smarter opponent team
        battle_result = battle(self.team, get_horse_team(self.turn_number))

        # update based on result of battle
        self.turn_number += 1
        if battle_result == BattleResult.TEAM1_WIN:
            self.num_wins += 1
        elif battle_result == BattleResult.TEAM2_WIN:
            self.hearts -= 1

        # recover lost heart if the round is early enough
        if (
            self.turn_number == TURN_AT_WHICH_THEY_GAIN_ONE_LOST_HEART
            and self.hearts < STARTING_HEARTS
        ):
            self.hearts += 1

        # since we moved onto the next round, we need to init it for the current round
        self.shop.init_shop_for_round(self.turn_number)

        if self.turn_number >= MAX_GAMES_LENGTH:
            return GameResult.TRUNCATED, battle_result
        # if the player has no more lives, they lose
        if self.hearts <= 0:
            return GameResult.LOSE, battle_result
        if self.num_wins == NUM_WINS_TO_WIN:
            return GameResult.WIN
        return GameResult.CONTINUE, battle_result

    # to help the model, you can only end turn if you have no gold
    # we can remove this restriction in the future?
    def end_turn_action_mask(self) -> np.ndarray:
        if self.shop.gold > 0:
            return np.zeros((1), dtype=bool)
        else:
            return np.ones((1), dtype=bool)

    def __repr__(self):
        stats = f"turn: {self.turn_number}, lives: {self.hearts}\u2764\ufe0f, num_actions_made: {self.num_actions_taken_in_turn}, wins: {self.num_wins}, team:\n"
        for pet in self.team.pets:
            stats += f"{pet}\n"
        return stats
