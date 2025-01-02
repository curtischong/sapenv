from all_types_and_consts import (
    MAX_ATTACK,
    MAX_TEAM_SIZE,
    BattleResult,
    Effect,
    Species,
    Trigger,
)
from pet import Pet
from pet_data import get_base_pet
from team import Team


def battle(my_team: Team, team2: Team) -> BattleResult:
    pets1 = (
        my_team.clone().get_pets_for_battle()
    )  # we need to clone the pets so the original team doesn't get modified
    pets2 = team2.clone().get_pets_for_battle()
    trigger_on_battle_start(pets1, pets2)

    while len(pets1) > 0 and len(pets2) > 0:
        # we need to explicitly get these attackers first because after the first attack_team call since the attacker pet might die.
        attacker1 = pets1[-1]
        attacker2 = pets2[-1]
        attack_team(attacker_pet=attacker1, receiving_team=pets2, attacking_team=pets1)
        attack_team(attacker_pet=attacker2, receiving_team=pets1, attacking_team=pets2)

    if len(pets1) == 0 and len(pets2) == 0:
        return BattleResult.TIE
    elif len(pets1) > 0:
        return BattleResult.WON_BATTLE
    else:
        return BattleResult.LOST_BATTLE


def trigger_on_battle_start(pets1: list[Pet], pets2: list[Pet]):
    on_battle_start_pets: list[
        tuple[int, Pet, bool]
    ] = []  # list of (pet_attack, pet, is_team1)
    print("pet1s", pets1)
    print("pet2s", pets2)

    for pet in pets1:
        on_battle_start_pets.append((pet.attack, pet, True))
    for pet in pets2:
        on_battle_start_pets.append((pet.attack, pet, False))

    # turn order is determined by the animal's attack. So sort by attack in descending order
    # https://youtu.be/pm1VpWt7LMA?si=veNCYgci5VAsTmYD&t=451
    # seems like on ties, it's random: https://www.reddit.com/r/superautopets/comments/uq8tdz/how_is_the_order_of_start_of_battle_abilities/?rdt=64622
    order = sorted(on_battle_start_pets, key=lambda x: x[0], reverse=True)

    # TODO: if the pet is killed by another pet, does its trigger still trigger?
    # the video above said: "the deer can be sniped before a whale eats it"
    # now trigger the on_battle_start triggers
    for _, pet, is_team1 in order:
        if is_team1:
            if pet in pets1 and len(pets2) > 0:  # ensure they are still alive
                pet.trigger(Trigger.ON_BATTLE_START, my_pets=pets1, enemy_pets=pets2)
        else:
            if pet in pets2 and len(pets1) > 0:
                pet.trigger(Trigger.ON_BATTLE_START, my_pets=pets2, enemy_pets=pets1)


def attack_team(
    attacker_pet: Pet, receiving_team: list[Pet], attacking_team: list[Pet]
):
    damage = attacker_pet.attack
    if attacker_pet.effect == Effect.MEAT_BONE:
        damage += 3
    elif attacker_pet.effect == Effect.STEAK:
        damage = max(damage + 20, MAX_ATTACK)
        attacker_pet.effect = Effect.NONE  # steak is only used once

    # trigger ON_BEFORE_ATTACK
    attacker_pet.trigger(Trigger.ON_BEFORE_ATTACK, my_pets=attacking_team)

    # trigger ON_FRIEND_AHEAD_ATTACKS
    if len(attacking_team) > 1:
        friend_behind_attacker = attacking_team[-2]
        friend_behind_attacker.trigger(
            Trigger.ON_FRIEND_AHEAD_ATTACKS,
            my_pets=attacking_team,
            enemy_pets=receiving_team,
        )

    # now apply the damage

    frontmost_pet = receiving_team[-1]
    second_pet = None
    if len(receiving_team) > 1:
        second_pet = receiving_team[-2]
    receive_damage(
        receiving_pet=frontmost_pet,
        attacking_pet=attacker_pet,
        damage=damage,
        receiving_team=receiving_team,
        opposing_team=attacking_team,
        is_in_battle=True,
    )

    if (
        attacker_pet.effect == Effect.CHILLI
        and second_pet
        and second_pet in receiving_team  # they are still alive in the team
    ):
        # attack the second pet if the chilli effect is active
        receive_damage(
            receiving_pet=second_pet,
            attacking_pet=attacker_pet,
            damage=5,
            receiving_team=receiving_team,
            opposing_team=attacking_team,
            is_in_battle=True,
        )

    attacker_pet.trigger(
        Trigger.ON_AFTER_ATTACK, my_pets=attacking_team, enemy_pets=receiving_team
    )


def receive_damage(
    receiving_pet: Pet,
    attacking_pet: Pet,
    damage: int,
    receiving_team: list[Pet],
    # this is called opposing_team, NOT attacking team (since the dealer of damage can be on your own team)
    opposing_team: list[Pet],
    is_in_battle: bool,
):
    if receiving_pet not in receiving_team:
        # this function was called (with older pets) but by now, the pet is dead. so don't do anything
        return

    if receiving_pet.effect == Effect.MELON:
        damage = max(damage - 20, 0)
        receiving_pet.effect = Effect.NONE  # melon is only used once
    elif receiving_pet.effect == Effect.GARLIC:
        damage = max(damage - 2, 1)  # yes. Garlic does a minimum of 1 damage
    receiving_pet.health -= damage

    if damage == 0:
        return  # early return to avoid computing on hurt effects

    receiving_pet.trigger(
        Trigger.ON_HURT,
        my_pets=receiving_team,
        enemy_pets=opposing_team,
        is_in_battle=is_in_battle,
    )
    for team_pet in receiving_team:
        if team_pet is not receiving_pet:
            team_pet.trigger(
                Trigger.ON_FRIEND_HURT,
                my_pets=receiving_team,
                enemy_pets=opposing_team,
                is_in_battle=is_in_battle,
            )
    if receiving_pet.health <= 0 or attacking_pet.effect == Effect.PEANUT:
        # TODO: not sure what should trigger first. the mushroom or the on faint affect?
        # https://www.reddit.com/r/superautopets/comments/12xtp8d/mushroom_faint_ability_ordering_different_for/?rdt=51575
        # I'll make the mushroom trigger last after all on faint effects are done (since it's what the sapai repo does)
        make_pet_faint(
            receiving_pet,
            my_pets=receiving_team,
            enemy_pets=opposing_team,
            is_in_battle=is_in_battle,
        )
        attacking_pet.trigger(
            Trigger.ON_KNOCK_OUT, my_pets=opposing_team, enemy_pets=receiving_team
        )


def make_pet_faint(
    pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet] | None, is_in_battle: bool
):
    idx_in_team = my_pets.index(pet)
    if is_in_battle:
        my_pets.pop(idx_in_team)  # remove the pet first to make room for other pets
    else:
        # e.g. when using a pill, we just set it to NONE (so the spot on the team becomes empty)
        my_pets[idx_in_team] = get_base_pet(Species.NONE)
    pet.trigger(
        Trigger.ON_FAINT,
        faint_pet_idx=idx_in_team,
        my_pets=my_pets,
        enemy_pets=enemy_pets,
        is_in_battle=is_in_battle,
    )
    for team_pet in my_pets:
        if team_pet is not pet:
            team_pet.trigger(
                Trigger.ON_FRIEND_FAINTS,
                faint_pet_idx=idx_in_team,
                my_pets=my_pets,
                is_in_battle=is_in_battle,
            )

    # now trigger the ON_FRIEND_AHEAD_FAINTS trigger
    if (
        idx_in_team > 0 and idx_in_team - 1 < len(my_pets)
    ):  # I think we need to evaluate idx_in_team - 1 < len(my_pets) because the on_friend_faints above may have altered the team
        my_pets[idx_in_team - 1].trigger(
            Trigger.ON_FRIEND_AHEAD_FAINTS,
            my_pets=my_pets,
            is_in_battle=is_in_battle,
        )

    if pet.effect == Effect.MUSHROOM:
        new_pet = get_base_pet(pet.species).set_stats(
            attack=1,
            health=1,
        )
        try_spawn_at_pos(new_pet, idx_in_team, my_pets, is_in_battle)
    elif pet.effect == Effect.BEE:
        new_pet = get_base_pet(Species.PET_SPAWN).set_stats(attack=1, health=1)
        try_spawn_at_pos(new_pet, idx_in_team, my_pets, is_in_battle)


def try_spawn_at_pos(pet_to_spawn: Pet, idx: int, pets: list[Pet], is_in_battle: bool):
    if len(pets) >= MAX_TEAM_SIZE:
        return
    if is_in_battle:
        # if it's in battle, the list is not a fixed size
        pets.insert(idx, pet_to_spawn)
    else:
        # if it's not in battle, the list is a fixed size.
        # one way is to just set the pet at the index. HOWEVER, we should try to "push" nearby pets into empty slots (to make room for the spawn)
        # e.g. when a ram is spawned, we should try to make room for the spawns
        # This is the right set of events. Because the alternative is that only one ram is spawned when there's room for two. It makes no sense since the player could've just shifted it before pilled the sheep to spawn the rams

        shift_team_to_allow_spawn(pets, idx)
        pets[idx] = pet_to_spawn
    for pet in pets:
        if pet is not pet_to_spawn:
            pet.trigger(
                Trigger.ON_FRIEND_SUMMONED,
                summoned_friend=pet_to_spawn,
                my_pets=pets,
                is_in_battle=is_in_battle,
            )


def shift_team_to_allow_spawn(pets: list[Pet], spawn_idx: int):
    if pets[spawn_idx].species == Species.NONE:
        # no need to shuffle positions
        return

    # 1) Search left for an empty slot
    for i in range(spawn_idx, -1, -1):
        if pets[i].species != Species.NONE:
            first_free_idx_to_left = i
            # Shift everything from i..spawn_idx one step to the left (to make room for hte spawn)
            for pet_idx in range(first_free_idx_to_left, spawn_idx):
                pets[pet_idx] = pets[pet_idx + 1]
            return

    # 2) otherwise, search right for an empty slot
    for j in range(spawn_idx + 1, len(pets)):
        if pets[j].species != Species.NONE:
            first_free_idx_to_right = j

            # Shift everything from spawn_idx...j one step to the right (to make room for hte spawn)
            for pet_idx in range(first_free_idx_to_right, spawn_idx, -1):
                pets[pet_idx] = pets[pet_idx - 1]
            return
    raise ValueError("Could not find a place to spawn")


def remove_empty_pets(pets: list[Pet]):
    res = []
    for pet in pets:
        if pet.species != Species.NONE:
            res.append(pet)
    return res
