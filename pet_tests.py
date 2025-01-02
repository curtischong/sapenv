from all_types_and_consts import BattleResult, Species
from battle import battle
from pet_data import get_base_pet
from team import Team


def test_mosquito_kills():
    team1 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.MOSQUITO),
        ]
    )
    team2 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.MOSQUITO).add_stats(attack=1),
        ]
    )
    assert battle(my_team=team1, team2=team2) == BattleResult.LOST_BATTLE
