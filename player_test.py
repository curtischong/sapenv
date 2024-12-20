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
    player.reorder_team(pet_start_idx=0, pet_end_idx=2)
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
    player.reorder_team(pet_start_idx=0, pet_end_idx=4)
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
    player.reorder_team(pet_start_idx=4, pet_end_idx=0)
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
    player.reorder_team(pet_start_idx=3, pet_end_idx=4)
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
