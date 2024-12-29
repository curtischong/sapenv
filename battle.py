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

        damage_pet(pet1, pets2)
        damage_pet(pet2, pets1)

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


def damage_pet(attacker_pet: Pet, receiving_team: list[Pet]):
    first_pet = receiving_team[-1]
    damage = attacker_pet.attack
    if attacker_pet.effect == Effect.MEAT_BONE:
        damage += 3
    elif attacker_pet.effect == Effect.STEAK:
        damage = max(damage + 20, MAX_ATTACK)
        attacker_pet.effect = Effect.NONE  # steak is only used once

    attacker_has_peanut_effect = attacker_pet.effect == Effect.PEANUT

    if attacker_pet.effect == Effect.CHILLI and len(receiving_team) > 1:
        second_pet = receiving_team[-2]
        receive_damage(
            pet=second_pet,
            damage=5,
            idx_in_team=len(receiving_team) - 2,
            receiving_team=receiving_team,
            attacker_has_peanut_effect=attacker_has_peanut_effect,
        )
    receive_damage(
        pet=first_pet,
        damage=damage,
        idx_in_team=len(receiving_team) - 1,
        receiving_team=receiving_team,
        attacker_has_peanut_effect=attacker_has_peanut_effect,
    )


def receive_damage(
    pet: Pet,
    damage: int,
    idx_in_team: int,
    team_pets: list[Pet],
    attacker_has_peanut_effect: bool,
):
    if pet.effect == Effect.MELON:
        damage = max(damage - 20, 0)
        pet.effect = Effect.NONE  # melon is only used once
    elif pet.effect == Effect.GARLIC:
        damage = max(damage - 2, 1)  # yes. Garlic does a minimum of 1 damage
    pet.health -= damage

    if damage == 0:
        return  # early return to avoid computing on hurt effects

    pet.on_hurt()
    if pet.health <= 0 or attacker_has_peanut_effect:
        # TODO: not sure what should trigger first. the mushroom or the on faint affect?
        # https://www.reddit.com/r/superautopets/comments/12xtp8d/mushroom_faint_ability_ordering_different_for/?rdt=51575
        # I'll make the mushroom trigger last after all on faint effects are done (since it's what the sapai repo does)
        trigger_on_faint(pet, idx_in_team, team_pets)


def trigger_on_faint(pet: Pet, idx_in_team: int, team_pets: list[Pet]):
    team_pets.pop(idx_in_team)  # remove the pet first to make room for other pets
    pet.on_faint()
    if pet.effect == Effect.MUSHROOM:
        new_pet = get_base_pet(pet.species).set_stats(
            attack=1,
            health=1,
        )
        try_spawn_at_pos(new_pet, idx_in_team, team_pets)
    elif pet.effect == Effect.BEE:
        new_pet = get_base_pet(Species.BEE)
        try_spawn_at_pos(new_pet, idx_in_team, team_pets)


def try_spawn_at_pos(pet: Pet, idx: int, pets: list[Pet]):
    if len(pets) >= 5:
        return
    pets.insert(idx, pet)
