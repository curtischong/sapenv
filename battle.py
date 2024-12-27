from all_types_and_consts import BattleResult
from pet import Pet
from team import Team


def battle_only_consider_health_and_attack(team1: Team, team2: Team) -> BattleResult:
    pets1 = (
        team1.clone().get_pets_without_none_species()
    )  # we need to clone the pets so the original team doesn't get modified
    pets2 = team2.clone().get_pets_without_none_species()

    while len(pets1) > 0 and len(pets2) > 0:
        pet1 = pets1[-1]
        pet2 = pets2[-1]

        attack_pets(pet1, pets2)
        attack_pets(pet2, pets1)

        if pet1.health <= 0:
            pets1.pop()
        if pet2.health <= 0:
            pets2.pop()

    if len(pets1) == 0 and len(pets2) == 0:
        return BattleResult.TIE
    elif len(pets1) > 0:
        return BattleResult.TEAM1_WIN
    else:
        return BattleResult.TEAM2_WIN


def battle_with_effects(team1: Team, team2: Team) -> BattleResult:
    pets1 = (
        team1.clone().get_pets_without_none_species()
    )  # we need to clone the pets so the original team doesn't get modified
    pets2 = team2.clone().get_pets_without_none_species()


def attack_pets(pet: Pet, opponent_pets: list[Pet]):
    top_pet = opponent_pets[-1]
    top_pet.health -= pet.attack
