import inspect
import math
import random
from typing import Any, Protocol, Type, get_type_hints
from all_types_and_consts import (
    MAX_ATTACK,
    MAX_HEALTH,
    BattleResult,
    Effect,
    Food,
    Species,
    Trigger,
)
from battle import receive_damage, try_spawn_at_pos
from pet import (
    Pet,
)
from shop import Shop
from team import Team
from pet_data import get_base_pet, species_to_pet_map, tier_3_pets


class OnSell(Protocol):
    def __call__(self, pet: Pet, shop: Shop, team: Team): ...


class OnBuy(Protocol):
    def __call__(self, pet: Pet, team: Team): ...


class OnFaint(Protocol):
    def __call__(
        self,
        pet: Pet,
        faint_pet_idx: int,
        my_pets: list[Pet],
        enemy_pets: list[Pet] | None,
        is_in_battle: bool,
    ): ...


class OnHurt(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet]): ...


class OnBattleStart(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]): ...


class OnLevelUp(Protocol):
    def __call__(self, pet: Pet, team: Team): ...


class OnFriendSummoned(Protocol):
    def __call__(self, pet: Pet, summoned_friend: Pet, is_in_battle: bool): ...


class OnEndTurn(Protocol):
    def __call__(self, pet: Pet, team: "Team", last_battle_result: BattleResult): ...


class OnTurnStart(Protocol):
    def __call__(self, pet: Pet, shop: Shop): ...


class OnFriendAheadAttacks(Protocol):
    def __call__(self, pet: Pet): ...


def on_sell_duck(pet: Pet, shop: Shop, team: Team):
    for slot in shop.slots:
        slot.pet.add_stats(health=pet.get_level())


def on_sell_beaver(pet: Pet, shop: Shop, team: Team):
    two_random_friends = team.get_random_pets(2, exclude_pet=pet)
    for pet in two_random_friends:
        pet.add_stats(attack=pet.get_level())


def on_sell_pigeon(pet: Pet, shop: Shop, team: Team):
    shop.num_foods[Food.BREAD_CRUMB] += pet.get_level()


def on_buy_otter(pet: Pet, team: Team):
    random_friends = team.get_random_pets(
        select_num_pets=pet.get_level(), exclude_pet=pet
    )
    for friend in random_friends:
        friend.add_stats(health=1)


def on_sell_pig(pet: Pet, shop: Shop, team: Team):
    shop.gold += pet.get_level()


def on_faint_ant(pet: Pet, faint_pet_idx: int, my_pets: list[Pet], is_in_battle: bool):
    pet_list = Team.get_random_pets_from_list(
        pets_list=my_pets, select_num_pets=1, exclude_pet=pet
    )
    if len(pet_list) > 0:
        stat_buff = pet.get_level()
        pet_list[0].add_stats(attack=stat_buff, health=stat_buff)


def on_battle_start_mosquito(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    random_enemy_pets = Team.get_random_pets_from_list(
        pets_list=enemy_pets, select_num_pets=pet.get_level()
    )
    for enemy_pet in random_enemy_pets:
        receive_damage(
            pet=enemy_pet,
            damage=1,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            attacker_has_peanut_effect=pet.effect == Effect.PEANUT,
        )


# this is called AFTER they level up
def on_level_up_fish(pet: Pet, team: Team):
    pet_level = pet.get_level()
    assert pet_level > 1
    stat_buff = pet_level - 1
    for pet in team.get_random_pets(2, exclude_pet=pet):
        pet.add_stats(attack=stat_buff, health=stat_buff)


def on_faint_cricket(
    pet: Pet, faint_pet_idx: int, my_pets: list[Pet], is_in_battle: bool
):
    cricket_spawn = get_base_pet(Species.CRICKET_SPAWN).set_stats(
        attack=pet.get_level(), health=pet.get_level()
    )
    try_spawn_at_pos(
        cricket_spawn, faint_pet_idx, pets=my_pets, is_in_battle=is_in_battle
    )


def on_friend_summoned_horse(pet: Pet, summoned_friend: Pet, is_in_battle: bool):
    assert pet is not summoned_friend
    attack_boost = pet.get_level()
    if is_in_battle:
        # if in battle, add stats instead of boost
        summoned_friend.add_stats(attack=attack_boost)
    else:
        summoned_friend.add_boost(attack=attack_boost)


def on_end_turn_snail(pet: Pet, team: Team, last_battle_result: BattleResult):
    # https://superautopets.fandom.com/wiki/Snail
    # it only triggers if it's a loss, not a draw
    # If Snail is bought on turn 1, the "last battle" will be considered a draw.
    # the snail does not buff itself: https://youtu.be/jk9z6yPkG3U?si=1Cwf11gtm4wgpaMr&t=451
    if last_battle_result != BattleResult.LOST_BATTLE:
        return

    buff_amount = pet.get_level()
    for my_pet in team.pets:
        if my_pet is not pet:
            my_pet.add_stats(attack=buff_amount, health=buff_amount)


def on_battle_start_crab(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    max_health_on_team = 0
    for my_pet in my_pets:
        max_health_on_team = max(max_health_on_team, my_pet.health)

    percentage_boost = 0.5 * pet.get_level()
    new_health = math.ceil(
        max_health_on_team * percentage_boost
    )  # ceil. so if all pets have 1 health, the crab will still have 1 health
    pet.health = min(new_health, MAX_HEALTH)


def on_turn_start_swan(pet: Pet, shop: Shop):
    shop.gold += pet.get_level()


def on_faint_rat(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    if not is_in_battle or enemy_pets is None:
        # enemy_pets is None if the rat fainted in the shop
        return

    num_spawns = pet.get_level()
    for _ in range(num_spawns):
        rat_spawn = get_base_pet(Species.RAT_SPAWN)

        # the rat always try to spawn it up front for the opponent
        front_idx = len(enemy_pets) - 1

        try_spawn_at_pos(rat_spawn, idx=front_idx, pets=enemy_pets, is_in_battle=True)


def on_faint_hedgehog(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    damage = 2 * pet.get_level()
    for my_pet in my_pets:
        if my_pet is not pet:
            receive_damage(
                pet=my_pet,
                damage=damage,
                receiving_team=my_pets,
                opposing_team=enemy_pets,
                attacker_has_peanut_effect=False,  # for now assume that the scorpion is the only pet with the peanut effect
            )

    if enemy_pets is None:
        return

    for enemy_pet in enemy_pets:
        receive_damage(
            pet=enemy_pet,
            damage=damage,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            attacker_has_peanut_effect=False,
        )


def on_hurt_peacock(
    pet: Pet,
    my_pets: list[Pet],
):
    attack_boost = 3 * pet.get_level()
    pet.attack = min(pet.attack + attack_boost, MAX_ATTACK)


def on_faint_flamingo(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    closest_friends_behind: list[Pet] = []
    for friend_idx in range(faint_pet_idx - 1, -1, -1):
        friend_pet = my_pets[friend_idx]
        if friend_pet.species != Species.NONE:
            closest_friends_behind.append(friend_pet)
        if len(closest_friends_behind) >= 2:
            break

    stat_boost = pet.get_level()
    for friend in closest_friends_behind:
        friend.add_stats(attack=stat_boost, health=stat_boost)


def on_turn_start_worm(
    pet: Pet,
    shop: Shop,
):
    # the apple the worm stocks is an ADDITIONAL food (doesn't take up a food slot)
    # https://youtu.be/T6moXKCurxw?si=HA5rgHUkSFPiPjh1&t=147
    match pet.get_level():
        case 1:
            shop.num_foods[Food.APPLE_2_COST] += 1
        case 2:
            shop.num_foods[Food.APPLE_2_COST_BETTER] += 1
        case 3:
            shop.num_foods[Food.APPLE_2_COST_BEST] += 1


def on_friend_ahead_attacks_kangaroo(pet: Pet):
    stat_buff = pet.get_level()
    pet.add_stats(attack=stat_buff, health=stat_buff)


def on_faint_spider(
    pet: Pet, faint_pet_idx: int, my_pets: list[Pet], is_in_battle: bool
):
    pet_to_spawn = random.choice(tier_3_pets).clone()
    stat = 2 * pet.get_level()

    # we need to ensure that the new pet has the proper experience since if it's spawned in the shop, it should have the proper experience
    match pet.get_level():
        case 1:
            new_spawn_experience = 1
        case 2:
            new_spawn_experience = 3
        case 3:
            new_spawn_experience = 6

    pet_to_spawn.set_stats_all(
        attack=stat, health=stat, experience=new_spawn_experience
    )
    try_spawn_at_pos(pet_to_spawn, faint_pet_idx, my_pets, is_in_battle)


def on_battle_start_dodo(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    # the dodo's attack is NOT cleared from it's own. it buffs the friend's attack https://youtu.be/7zymvXc9OrU?si=KVVqzWX1u6-z_LCc&t=76
    percentage_amount_to_give = 0.5 * pet.get_level()

    # use ceil. so if the dodo has 1 attack, we give 1 attack to the friend
    attack_to_give_to_friend = math.ceil(percentage_amount_to_give * pet.attack)

    pet_idx = my_pets.index(pet)
    if pet_idx == len(my_pets) - 1:
        # there are no friends ahead to give the attack to. We don't have to worry about none species here since it's the start of the battle
        return
    pet_ahead = my_pets[pet_idx + 1]
    pet_ahead.add_stats(attack=attack_to_give_to_friend)


def on_faint_badger(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    percentage_damage_to_deal = 0.5 * pet.get_level()
    damage_to_deal = math.ceil(percentage_damage_to_deal * pet.attack)

    ahead_idx = faint_pet_idx + 1
    if ahead_idx < len(my_pets):
        pet_ahead = my_pets[ahead_idx]
        if pet_ahead.species != Species.NONE:
            receive_damage(
                pet=pet_ahead,
                damage=damage_to_deal,
                receiving_team=my_pets,
                opposing_team=enemy_pets,
                attacker_has_peanut_effect=False,
            )
    else:  # else: the badger is at the front of the team
        if is_in_battle and len(enemy_pets) > 0:
            pet_ahead = enemy_pets[-1]
            receive_damage(
                pet=pet_ahead,
                damage=damage_to_deal,
                receiving_team=enemy_pets,
                opposing_team=my_pets,
                attacker_has_peanut_effect=False,
            )
        # else: there is no pet ahead to deal damage to

    # now deal damage to the pet behind (you can only damage your own team)
    if faint_pet_idx > 0:
        pet_behind = my_pets[faint_pet_idx - 1]
        receive_damage(
            pet=pet_behind,
            damage=damage_to_deal,
            receiving_team=my_pets,
            opposing_team=enemy_pets,
            attacker_has_peanut_effect=False,
        )


def on_battle_start_dolphin(
    pet: Pet,
    my_pets: list[Pet],
    enemy_pets: list[Pet],
):
    num_times_this_triggers = pet.get_level()

    for _ in range(num_times_this_triggers):
        lowest_health_enemy_pet = None
        lowest_health = MAX_HEALTH + 1
        for enemy_pet in enemy_pets:
            if enemy_pet.health < lowest_health:
                lowest_health_enemy_pet = enemy_pet
                lowest_health = enemy_pet.health

        if lowest_health_enemy_pet is None:
            return

        # now deal damage to the lowest health enemy pet
        receive_damage(
            pet=lowest_health_enemy_pet,
            damage=4,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            attacker_has_peanut_effect=False,
        )


def set_pet_triggers():
    # fmt: off
    # tier 1
    species_to_pet_map[Species.DUCK].set_trigger(Trigger.ON_SELL, on_sell_duck)
    species_to_pet_map[Species.BEAVER].set_trigger(Trigger.ON_SELL, on_sell_beaver)
    species_to_pet_map[Species.PIGEON].set_trigger(Trigger.ON_SELL, on_sell_pigeon)
    species_to_pet_map[Species.OTTER].set_trigger(Trigger.ON_BUY, on_buy_otter)
    species_to_pet_map[Species.PIG].set_trigger(Trigger.ON_SELL, on_sell_pig)
    species_to_pet_map[Species.ANT].set_trigger(Trigger.ON_FAINT, on_faint_ant)
    species_to_pet_map[Species.MOSQUITO].set_trigger( Trigger.ON_BATTLE_START, on_battle_start_mosquito)
    species_to_pet_map[Species.FISH].set_trigger(Trigger.ON_LEVEL_UP, on_level_up_fish)
    species_to_pet_map[Species.CRICKET].set_trigger(Trigger.ON_FAINT, on_faint_cricket)
    species_to_pet_map[Species.HORSE].set_trigger(Trigger.ON_FRIEND_SUMMONED, on_friend_summoned_horse)

    # tier 2
    species_to_pet_map[Species.SNAIL].set_trigger(Trigger.ON_END_TURN, on_end_turn_snail)
    species_to_pet_map[Species.CRAB].set_trigger(Trigger.ON_BATTLE_START, on_battle_start_crab)
    species_to_pet_map[Species.SWAN].set_trigger(Trigger.ON_TURN_START, on_turn_start_swan)
    species_to_pet_map[Species.RAT].set_trigger(Trigger.ON_FAINT, on_faint_rat)
    species_to_pet_map[Species.HEDGEHOG].set_trigger(Trigger.ON_FAINT, on_faint_hedgehog)
    species_to_pet_map[Species.PEACOCK].set_trigger(Trigger.ON_HURT, on_hurt_peacock)
    species_to_pet_map[Species.FLAMINGO].set_trigger(Trigger.ON_FAINT, on_faint_flamingo)
    species_to_pet_map[Species.WORM].set_trigger(Trigger.ON_TURN_START, on_turn_start_worm)
    species_to_pet_map[Species.KANGAROO].set_trigger(Trigger.ON_FRIEND_AHEAD_ATTACKS, on_friend_ahead_attacks_kangaroo)
    species_to_pet_map[Species.SPIDER].set_trigger(Trigger.ON_FAINT, on_faint_spider)

    # tier 3
    species_to_pet_map[Species.DODO].set_trigger(Trigger.ON_BATTLE_START, on_battle_start_dodo)
    species_to_pet_map[Species.BADGER].set_trigger(Trigger.ON_FAINT, on_faint_badger)
    species_to_pet_map[Species.DOLPHIN].set_trigger(Trigger.ON_BATTLE_START, on_battle_start_dolphin)

    # fmt: on


class CallableProtocol(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


# validate on run time that all the triggers follow the correct interface
def validate_protocol(func: Any, protocol: Type[CallableProtocol]) -> None:
    """
    Validates whether a callable conforms to a given protocol.

    Parameters:
    - func: The callable to validate.
    - protocol: The protocol to validate against.

    Raises:
    - TypeError: If the callable does not conform to the protocol.
    """
    func_signature = inspect.signature(func)
    protocol_hints = get_type_hints(
        protocol.__call__
    )  # Extract the type hints of the protocol's __call__

    protocol_signature = inspect.Signature(
        parameters=[
            inspect.Parameter(
                name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=annotation
            )
            for name, annotation in protocol_hints.items()
            if name != "return"
        ],
        return_annotation=protocol_hints.get("return", inspect.Signature.empty),
    )

    # Compare the function's signature with the protocol's signature
    if func_signature != protocol_signature:
        raise TypeError(
            f"The function {func.__name__} does not conform to the protocol {protocol.__name__}.\n"
            f"Expected: {protocol_signature}\nGot: {func_signature}"
        )


trigger_to_protocol_type = {
    Trigger.ON_SELL: OnSell,
    Trigger.ON_BUY: OnBuy,
    Trigger.ON_FAINT: OnFaint,
    Trigger.ON_HURT: OnHurt,
    Trigger.ON_BATTLE_START: OnBattleStart,
    Trigger.ON_LEVEL_UP: OnLevelUp,
    Trigger.ON_FRIEND_SUMMONED: OnFriendSummoned,
    Trigger.ON_END_TURN: OnEndTurn,
    Trigger.ON_TURN_START: OnTurnStart,
    Trigger.ON_FRIEND_AHEAD_ATTACKS: OnFriendAheadAttacks,
}


def validate_trigger_protocols():
    for pet in species_to_pet_map.values():
        for trigger, trigger_fn in pet._triggers.items():
            protocol_type = trigger_to_protocol_type[trigger]
            validate_protocol(trigger_fn, protocol_type)
