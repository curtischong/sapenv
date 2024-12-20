from all_types_and_consts import BattleResult, Species
from battle import battle
from pet import Pet
from pet_data import get_base_pet
from team import Team


def test_single_pet_can_beat_team_with_more_pets():
    team1 = Team(
        [
            get_base_pet(Species.SNAIL),
            get_base_pet(Species.SNAIL),
            get_base_pet(Species.SNAIL),
            get_base_pet(Species.SNAIL),
            get_base_pet(Species.SNAIL),
        ]
    )
    team2 = Team(
        [
            get_base_pet(Species.PIG).add_stats(attack=10, health=40),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
        ]
    )
    assert battle(team1, team2) == BattleResult.TEAM2_WIN


def test_pets_attack_in_proper_order():
    # This is supposed to be a tie.
    # but if the battle happens in reverse, team2 will win
    # note: the last index is FIRST to attack
    team1 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.PIG).set_stats(attack=1, health=2),
            get_base_pet(Species.PIG).set_stats(attack=1, health=2),
        ]
    )
    team2 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.SNAIL).set_stats(attack=2, health=1),
            get_base_pet(Species.SNAIL).set_stats(attack=2, health=1),
            get_base_pet(Species.SNAIL).set_stats(attack=1, health=1),
        ]
    )
    assert battle(team1, team2) == BattleResult.TIE
