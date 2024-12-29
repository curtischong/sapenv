from all_types_and_consts import BattleResult, Effect
from pet import Pet
from team import Team


def battle(my_team: Team, team2: Team) -> BattleResult:
    pets1 = (
        my_team.clone().get_pets_for_battle()
    )  # we need to clone the pets so the original team doesn't get modified
    pets2 = team2.clone().get_pets_for_battle()

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
        return BattleResult.WON_BATTLE
    else:
        return BattleResult.LOST_BATTLE


def attack_pets(pet: Pet, opponent_pets: list[Pet]):
    top_pet = opponent_pets[-1]
    top_pet.health -= pet.attack

    # on attack modifier:
    # chillie: hit the opponent behind it
    # meat bone: do more attack (but this is just a buff)


def damage_pet(attacker_pet: Pet, receiving_team: Team):
    first_pet = receiving_team.pets[-1]
    damage = attacker_pet.attack
    if attacker_pet.effect == Effect.MEAT_BONE:
        damage += 3

    if attacker_pet.effect == Effect.CHILLI and len(receiving_team.pets) > 1:
        second_pet = receiving_team.pets[-2]
        receive_damage(second_pet, damage)
    receive_damage(first_pet, damage)


def receive_damage(pet: Pet, damage: int, idx_in_team: int, team: Team):
    if pet.effect == Effect.MELON:
        damage = max(damage - 20, 0)
        pet.effect = Effect.NONE  # melon is only used once
    elif pet.effect == Effect.GARLIC:
        damage = max(damage - 2, 0)
    pet.health -= damage
    pet.on_hurt()
    if pet.health <= 0:
        pet.on_death()
        team.pets.pop(idx_in_team)
