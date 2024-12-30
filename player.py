import itertools
from all_types_and_consts import (
    MAX_GAMES_LENGTH,
    MAX_SHOP_LINKED_SLOTS,
    MAX_TEAM_SIZE,
    NUM_WINS_TO_WIN,
    PET_COST,
    ROLL_COST,
    STARTING_HEARTS,
    TURN_AT_WHICH_THEY_GAIN_ONE_LOST_HEART,
    ActionReturn,
    BattleResult,
    Food,
    GameResult,
    Species,
    MAX_SHOP_SLOTS,
    Trigger,
    foods_that_apply_globally,
    foods_for_pet,
)
from battle import battle
from food_triggers import trigger_food_for_pet, trigger_food_globally
from opponent_db import OpponentDB
from pet_data import get_base_pet
from shop import Shop
from team import Team
import numpy as np


class Player:
    def __init__(self, team: Team):
        self.team = team
        self.shop = Shop()
        self.turn_number = 0
        self.num_wins = 0
        self.num_actions_taken_in_turn = 0
        self.hearts = STARTING_HEARTS
        self.opponent_db: OpponentDB = None

    @staticmethod
    def init_starting_player(opponent_db: OpponentDB):
        player = Player(Team.init_starting_team())
        player.opponent_db = opponent_db
        player.shop.init_shop_for_round(round_number=1)
        return player

    def reorder_team_action(self, start_idx: int, end_idx: int):
        pets = self.team.pets
        assert pets[start_idx].species != Species.NONE
        assert start_idx != end_idx

        # Remove the pet from the old position
        pet_to_move = pets.pop(start_idx)

        # Insert it into the new position
        pets.insert(end_idx, pet_to_move)

        return True

    def reorder_team_action_mask(self) -> np.ndarray:
        # return np.zeros( (MAX_TEAM_SIZE, MAX_TEAM_SIZE), dtype=bool)  # comment this out to disable toggle freeze slot
        mask = np.ones((MAX_TEAM_SIZE, MAX_TEAM_SIZE), dtype=bool)

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
    def combine_pets_action(self, pet1_idx: int, pet2_idx: int):
        assert pet1_idx != pet2_idx

        pet1 = self.team.pets[pet1_idx]
        pet2 = self.team.pets[pet2_idx]

        assert pet1.species == pet2.species
        assert pet1.species != Species.NONE
        assert pet1.get_level() < 3 and pet2.get_level() < 3

        new_pet = pet1.combine_onto(pet2, self.shop)
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
            self.team.pets[target_team_idx] = bought_pet.combine_onto(
                pet_at_team_idx, self.shop
            )
        else:
            self.team.pets[target_team_idx] = bought_pet

        # trigger on_buy AFTER the pet is added to the team (so the proper level is considered)
        bought_pet = self.team.pets[target_team_idx]
        bought_pet.trigger(Trigger.ON_BUY, team=self.team)
        return {ActionReturn.BOUGHT_PET_SPECIES: shop_pet_species}

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
            self.team.pets[target_team_idx] = bought_pet.combine_onto(
                pet_at_team_idx, self.shop
            )
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

    def buy_food_action(self, food_idx: int):
        food_type = foods_that_apply_globally[food_idx]
        self.shop.buy_food(food_type)
        trigger_food_globally(food_type, self.team, self.shop)

    def buy_food_action_mask(self) -> np.ndarray:
        # return np.zeros((len(foods_that_apply_globally)), dtype=bool)
        mask = np.zeros((len(foods_that_apply_globally)), dtype=bool)
        for i, food_type in enumerate(foods_that_apply_globally):
            if (
                self.shop.num_foods[food_type] > 0  # food is available
                and self.shop.food_cost(food_type) <= self.shop.gold  # can afford
            ):
                mask[i] = True
        return mask

    def buy_food_for_pet_action(self, food_idx: int, pet_idx: int):
        food_type = foods_for_pet[food_idx]
        self.shop.buy_food_for_pet(food_type)
        assert self.team.pets[pet_idx].species != Species.NONE
        trigger_food_for_pet(food_type, self.team, pet_idx)

    def buy_food_for_pet_action_mask(self) -> np.ndarray:
        # return np.zeros( (len(foods_for_pet), MAX_TEAM_SIZE), dtype=bool)
        mask = np.zeros((len(foods_for_pet), MAX_TEAM_SIZE), dtype=bool)
        for i, food_type in enumerate(foods_for_pet):
            if (
                self.shop.num_foods[food_type] == 0  # food is not available
                or self.shop.food_cost(food_type) > self.shop.gold  # too poor to buy
            ):
                continue
            non_empty_pets = [pet.species != Species.NONE for pet in self.team.pets]
            mask[i] = non_empty_pets
        return mask

    def freeze_food_action(self, food_type_idx: int):
        food_type = Food(food_type_idx)
        self.shop.freeze_food(food_type)

    def freeze_food_action_mask(self) -> np.ndarray:
        # return np.zeros((len(Food)), dtype=bool)
        mask = np.zeros((len(Food)), dtype=bool)
        for food_type in self.shop.num_foods:
            if self.shop.num_frozen_foods[food_type] < self.shop.num_foods[food_type]:
                mask[food_type.value] = True
        return mask

    def unfreeze_food_action(self, food_type_idx: Food):
        food_type = Food(food_type_idx)
        self.shop.unfreeze_food(food_type)

    def unfreeze_food_action_mask(self) -> np.ndarray:
        # return np.zeros((len(Food)), dtype=bool)
        mask = np.zeros((len(Food)), dtype=bool)
        for food_type in self.shop.num_frozen_foods:
            if self.shop.num_frozen_foods[food_type] > 0:
                mask[food_type.value] = True
        return mask

    def sell_pet_action(self, idx: int):
        pet = self.team.pets[idx]
        pet_species = pet.species
        assert pet_species != Species.NONE
        pet.trigger(Trigger.ON_SELL, shop=self.shop, team=self.team)
        self.shop.gold += pet.get_level()

        self.team.pets[idx] = get_base_pet(Species.NONE)
        return {ActionReturn.SOLD_PET_SPECIES: pet_species}

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
        battle_result = battle(
            self.team,
            self.opponent_db.get_opponent_similar_in_stregth(
                team=self.team,
                num_wins=self.num_wins,
                num_games_played=self.turn_number,
                num_lives_remaining=self.hearts,
            ),
        )

        # reset temporary buffs
        for pet in self.team.pets:
            pet.attack_boost = 0
            pet.health_boost = 0

        # update based on result of battle
        self.turn_number += 1
        if battle_result == BattleResult.WON_BATTLE:
            self.num_wins += 1
        elif battle_result == BattleResult.LOST_BATTLE:
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
            game_result = GameResult.TRUNCATED
        # if the player has no more lives, they lose
        elif self.hearts <= 0:
            game_result = GameResult.LOSE
        elif self.num_wins == NUM_WINS_TO_WIN:
            game_result = GameResult.WIN
        else:
            game_result = GameResult.CONTINUE

        return {
            ActionReturn.GAME_RESULT: game_result,
            ActionReturn.BATTLE_RESULT: battle_result,
        }

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
