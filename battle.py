from all_types_and_consts import MAX_ATTACK, BattleResult, Effect, Species
from pet import Pet
from pet_data import get_base_pet
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
    elif attacker_pet.effect == Effect.STEAK:
        damage = max(damage + 20, MAX_ATTACK)
        attacker_pet.effect = Effect.NONE  # steak is only used once

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
        # TODO: not sure what should trigger first. the mushroom or the on faint affect?
        # https://www.reddit.com/r/superautopets/comments/12xtp8d/mushroom_faint_ability_ordering_different_for/?rdt=51575
        # I'll make the mushroom trigger last after all on faint effects are done (since it's what the sapai repo does)
        pet.on_faint()
        if pet.effect == Effect.MUSHROOM:
            team.pets[idx_in_team] = get_base_pet(pet.species).set_stats(
                attack=1,
                health=1,
            )
        elif pet.effect == Effect.BEE:
            team.pets[idx_in_team] = get_base_pet(Species.BEE)
        team.pets.pop(idx_in_team)


def try_spawn_at_pos(pet: Pet, idx: int, team: Team):
    if len(team.pets) >= 5:
        return
    team.pets.insert(idx, pet)
