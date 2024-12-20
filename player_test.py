import pytest
from all_types_and_consts import Species
from pet_data import get_base_pet
from player import Player
from team import Team


@pytest.fixture
def original_team() -> Team:
    return Team(
        pets=[
            get_base_pet(Species.DUCK),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.BEAVER),
            get_base_pet(Species.PIGEON),
        ]
    )


@pytest.fixture
def player(original_team: Team) -> Player:
    # Each test gets a new player instance with a fresh copy of original_team
    return Player(original_team)


def test_rearrange_team_move_start_to_middle(player: Player):
    player.reorder_team_action(pet_start_idx=0, pet_end_idx=2)
    desired_pet_order_team = Team(
        pets=[
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.DUCK),
            get_base_pet(Species.BEAVER),
            get_base_pet(Species.PIGEON),
        ]
    )
    assert player.team == desired_pet_order_team


def test_rearrange_team_move_start_to_end(player: Player):
    player.reorder_team_action(pet_start_idx=0, pet_end_idx=4)
    desired_pet_order_team = Team(
        pets=[
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.BEAVER),
            get_base_pet(Species.PIGEON),
            get_base_pet(Species.DUCK),
        ]
    )
    assert player.team == desired_pet_order_team


def test_rearrange_team_move_end_to_start(player: Player):
    player.reorder_team_action(pet_start_idx=4, pet_end_idx=0)
    desired_pet_order_team = Team(
        pets=[
            get_base_pet(Species.PIGEON),
            get_base_pet(Species.DUCK),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.BEAVER),
        ]
    )
    assert player.team == desired_pet_order_team


def test_rearrange_team_move_middle_to_end(player: Player):
    player.reorder_team_action(pet_start_idx=3, pet_end_idx=4)
    desired_pet_order_team = Team(
        pets=[
            get_base_pet(Species.DUCK),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.PIGEON),
            get_base_pet(Species.BEAVER),
        ]
    )
    assert player.team == desired_pet_order_team


def test_combine_pets_moves_pet1_to_pet2():
    player = Player(
        Team(
            pets=[
                get_base_pet(Species.BEAVER).add_stats(attack=2, health=1),
                get_base_pet(Species.BEAVER),
                get_base_pet(Species.NONE),
                get_base_pet(Species.NONE),
                get_base_pet(Species.NONE),
            ]
        )
    )
    player.combine_pets_action(pet1_idx=0, pet2_idx=1)

    new_beaver = get_base_pet(Species.BEAVER).add_stats(attack=3, health=2)
    new_beaver.experience = 2

    desired_team = Team(
        pets=[
            get_base_pet(Species.NONE),
            new_beaver,
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
        ]
    )
    assert player.team == desired_team


def test_buy_pet(player: Player):
    player.shop.init_shop_for_round(3)
    player.buy_pet_at_slot(slot_idx=2, target_team_idx=2)
    assert player.team.pets[2].species != Species.NONE
