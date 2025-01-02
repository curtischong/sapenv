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


# pet1s [BEAVER: 3🗡 2❤️ lvl1-1, DUCK: 7🗡 8❤️ lvl1-1, BLOWFISH: 3🗡 6❤️ lvl1-1]
# pet2s [BEAVER: 3🗡 2❤️ lvl1-1, MOSQUITO: 2🗡 2❤️ lvl1-1]
# my_pets listed [] MOSQUITO: 2🗡 -1❤️ lvl1-1
def test_battle_start2():
    set_pet_triggers()
    validate_trigger_protocols()
    validate_can_trigger_in_shop_or_battle_triggers_have_is_in_battle_kwarg()
    team1 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.BEAVER).set_stats(attack=3, health=2),
            get_base_pet(Species.DUCK).set_stats(attack=7, health=8),
            get_base_pet(Species.BLOWFISH).set_stats(attack=3, health=6),
        ]
    )
    team2 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.BEAVER).set_stats(attack=3, health=2),
            get_base_pet(Species.MOSQUITO).set_stats(attack=2, health=2),
        ]
    )
    for _ in range(100):
        assert battle(my_team=team1, team2=team2) == BattleResult.WON_BATTLE


if __name__ == "__main__":
    test_battle_start2()
