from all_types_and_consts import BattleResult, Species
from battle import battle
from pet_data import get_base_pet
from pet_triggers import (
    set_pet_triggers,
    validate_can_trigger_in_shop_or_battle_triggers_have_is_in_battle_kwarg,
    validate_trigger_protocols,
)
from team import Team


def test_battle_start_prioritizes_higher_attack():
    set_pet_triggers()
    validate_trigger_protocols()
    validate_can_trigger_in_shop_or_battle_triggers_have_is_in_battle_kwarg()
    team1 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.MOSQUITO).set_stats(attack=1, health=1),
        ]
    )
    team2 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.MOSQUITO).set_stats(attack=2, health=1),
        ]
    )
    assert battle(my_team=team1, team2=team2) == BattleResult.LOST_BATTLE
