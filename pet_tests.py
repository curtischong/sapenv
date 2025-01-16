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


def test_hedgehog_takes_out_all_pets():
    set_pet_triggers()
    validate_trigger_protocols()
    validate_can_trigger_in_shop_or_battle_triggers_have_is_in_battle_kwarg()
    team1 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.HEDGEHOG).set_stats(attack=2, health=1),
        ]
    )
    team2 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.MOSQUITO).set_stats(attack=3, health=1),
            get_base_pet(Species.MOSQUITO).set_stats(attack=1, health=1),
        ]
    )
    assert battle(my_team=team1, team2=team2) == BattleResult.TIE


# pet1s [BEAVER: 3🗡 2❤️ lvl1-1, DUCK: 7🗡 8❤️ lvl1-1, BLOWFISH: 3🗡 6❤️ lvl1-1]
# pet2s [BEAVER: 3🗡 2❤️ lvl1-1, MOSQUITO: 2🗡 2❤️ lvl1-1]
# my_pets listed [] MOSQUITO: 2🗡 -1❤️ lvl1-1
def test_blowfish_battle_start():
    set_pet_triggers()
    validate_trigger_protocols()
    validate_can_trigger_in_shop_or_battle_triggers_have_is_in_battle_kwarg()
    team1 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.BLOWFISH).set_stats(attack=2, health=6),
        ]
    )
    team2 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.MOSQUITO).set_stats(attack=1, health=1),
        ]
    )
    assert battle(my_team=team1, team2=team2) == BattleResult.WON_BATTLE


"""
pet1s----- [OTTER: 2🗡 4❤️ lvl1-1, ANT: 4🗡 7❤️ lvl2-0, RAT: 5🗡 8❤️ lvl1-1, BLOWFISH: 4🗡 7❤️ lvl1-1, CRICKET: 4🗡 6❤️ lvl1-1]
pet2s----- [MOSQUITO: 2🗡 2❤️ lvl1-1, BEAVER: 3🗡 2❤️ lvl1-1]
RAT: 5🗡 8❤️ lvl1-1 pets1 [OTTER: 2🗡 4❤️ lvl1-1, ANT: 4🗡 7❤️ lvl2-0, RAT: 5🗡 8❤️ lvl1-1, BLOWFISH: 4🗡 7❤️ lvl1-1, CRICKET: 4🗡 6❤️ lvl1-1]
ANT: 4🗡 7❤️ lvl2-0 pets1 [OTTER: 2🗡 4❤️ lvl1-1, ANT: 4🗡 7❤️ lvl2-0, RAT: 5🗡 8❤️ lvl1-1, BLOWFISH: 4🗡 7❤️ lvl1-1, CRICKET: 4🗡 6❤️ lvl1-1]
BLOWFISH: 4🗡 7❤️ lvl1-1 pets1 [OTTER: 2🗡 4❤️ lvl1-1, ANT: 4🗡 7❤️ lvl2-0, RAT: 5🗡 8❤️ lvl1-1, BLOWFISH: 4🗡 7❤️ lvl1-1, CRICKET: 4🗡 6❤️ lvl1-
1]
CRICKET: 4🗡 6❤️ lvl1-1 pets1 [OTTER: 2🗡 4❤️ lvl1-1, ANT: 4🗡 7❤️ lvl2-0, RAT: 5🗡 8❤️ lvl1-1, BLOWFISH: 4🗡 7❤️ lvl1-1, CRICKET: 4🗡 6❤️ lvl1-1
]
BEAVER: 3🗡 2❤️ lvl1-1 pets2 [MOSQUITO: 2🗡 2❤️ lvl1-1, BEAVER: 3🗡 2❤️ lvl1-1]
OTTER: 2🗡 4❤️ lvl1-1 pets1 [OTTER: 2🗡 4❤️ lvl1-1, ANT: 4🗡 7❤️ lvl2-0, RAT: 5🗡 8❤️ lvl1-1, BLOWFISH: 4🗡 7❤️ lvl1-1, CRICKET: 4🗡 6❤️ lvl1-1]
MOSQUITO: 2🗡 2❤️ lvl1-1 pets2 [MOSQUITO: 2🗡 2❤️ lvl1-1, BEAVER: 3🗡 2❤️ lvl1-1]
my_pets listed [] MOSQUITO: 2🗡 -1❤️ lvl1-1 {'my_pets': [], 'enemy_pets': [OTTER: 2🗡 4❤️ lvl1-1, ANT: 4🗡 7❤️ lvl2-0, RAT: 5🗡 7❤️ lvl1-1, B
LOWFISH: 4🗡 6❤️ lvl1-1, CRICKET: 4🗡 6❤️ lvl1-1]}
"""


def test_no_battle_start_crash():
    set_pet_triggers()
    validate_trigger_protocols()
    validate_can_trigger_in_shop_or_battle_triggers_have_is_in_battle_kwarg()
    team1 = Team(
        [
            get_base_pet(Species.OTTER).set_stats(attack=2, health=4),
            get_base_pet(Species.ANT).set_stats(attack=4, health=7).set_level(2),
            get_base_pet(Species.RAT).set_stats(attack=5, health=8),
            get_base_pet(Species.BLOWFISH).set_stats(attack=4, health=7),
            get_base_pet(Species.CRICKET).set_stats(attack=4, health=6),
        ]
    )
    team2 = Team(
        [
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.MOSQUITO).set_stats(attack=2, health=2),
            get_base_pet(Species.BEAVER).set_stats(attack=3, health=2),
        ]
    )
    for _ in range(20000):
        assert battle(my_team=team1, team2=team2) == BattleResult.WON_BATTLE


if __name__ == "__main__":
    # test_hedgehog_takes_out_all_pets()
    # test_blowfish_battle_start()
    test_no_battle_start_crash()
