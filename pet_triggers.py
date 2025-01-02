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
    can_trigger_in_shop_or_battle,
)
from battle import make_pet_faint, receive_damage, try_spawn_at_pos
from pet import (
    Pet,
)
from pet_trigger_utils import (
    get_experience_for_level,
    get_nearest_friends_ahead,
    get_nearest_friends_behind,
    get_nearest_friends_behind_idx,
    get_pet_with_highest_health,
    get_pet_with_lowest_health,
)
from shop import FoodShopSlot, Shop
from team import Team
from pet_data import get_base_pet, species_to_pet_map, tier_1_pet_species, tier_3_pets


class OnSell(Protocol):
    def __call__(self, pet: Pet, shop: Shop, team: Team): ...


class OnBuy(Protocol):
    def __call__(self, pet: Pet, team: Team, shop: Shop): ...


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
    def __call__(
        self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet], is_in_battle: bool
    ): ...


class OnBattleStart(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]): ...


class OnLevelUp(Protocol):
    def __call__(self, pet: Pet, team: Team): ...


class OnFriendSummoned(Protocol):
    def __call__(
        self, pet: Pet, summoned_friend: Pet, my_pets: list[Pet], is_in_battle: bool
    ): ...


class OnEndTurn(Protocol):
    def __call__(self, pet: Pet, team: Team, last_battle_result: BattleResult): ...


class OnTurnStart(Protocol):
    def __call__(self, pet: Pet, team: Team, shop: Shop): ...


class OnFriendAheadAttacks(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]): ...


class OnAfterAttack(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]): ...


class OnFriendlyAteFood(Protocol):
    def __call__(self, pet: Pet, pet_that_ate_food: Pet, team: Team): ...


class OnFriendAheadFaints(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet], is_in_battle: bool): ...


class OnKnockOut(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]): ...


class OnFriendFaints(Protocol):
    def __call__(
        self, pet: Pet, faint_pet_idx: int, my_pets: list[Pet], is_in_battle: bool
    ): ...


class OnBeforeAttack(Protocol):
    def __call__(self, pet: Pet): ...


class OnFriendHurt(Protocol):
    def __call__(
        self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet], is_in_battle: bool
    ): ...


class OnFriendBought(Protocol):
    def __call__(self, pet: Pet, bought_pet: Pet, team: Team): ...


def on_sell_duck(pet: Pet, shop: Shop, team: Team):
    for slot in shop.slots:
        slot.pet.add_stats(health=pet.get_level())


def on_sell_beaver(pet: Pet, shop: Shop, team: Team):
    two_random_friends = team.get_random_pets(2, exclude_pet=pet)
    for pet in two_random_friends:
        pet.add_stats(attack=pet.get_level())


def on_sell_pigeon(pet: Pet, shop: Shop, team: Team):
    for _ in range(pet.get_level()):
        shop.food_slots.append(FoodShopSlot(Food.BREAD_CRUMB))


def on_buy_otter(pet: Pet, team: Team, shop: Shop):
    random_friends = team.get_random_pets(
        select_num_pets=pet.get_level(), exclude_pet=pet
    )
    for friend in random_friends:
        friend.add_stats(health=1)


def on_sell_pig(pet: Pet, shop: Shop, team: Team):
    shop.gold += pet.get_level()


def on_faint_ant(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
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
            receiving_pet=enemy_pet,
            attacking_pet=pet,
            damage=1,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            is_in_battle=True,
        )


# this is called AFTER they level up
def on_level_up_fish(pet: Pet, team: Team):
    pet_level = pet.get_level()
    assert pet_level > 1
    stat_buff = pet_level - 1
    for pet in team.get_random_pets(2, exclude_pet=pet):
        pet.add_stats(attack=stat_buff, health=stat_buff)


def on_faint_cricket(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    cricket_spawn = get_base_pet(Species.PET_SPAWN).set_stats(
        attack=pet.get_level(), health=pet.get_level()
    )
    try_spawn_at_pos(
        cricket_spawn, faint_pet_idx, pets=my_pets, is_in_battle=is_in_battle
    )


def on_friend_summoned_horse(
    pet: Pet, summoned_friend: Pet, my_pets: list[Pet], is_in_battle: bool
):
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
    highest_health_pet = get_pet_with_highest_health(my_pets)

    percentage_boost = 0.5 * pet.get_level()
    new_health = math.ceil(
        highest_health_pet.health * percentage_boost
    )  # ceil. so if all pets have 1 health, the crab will still have 1 health
    pet.health = min(new_health, MAX_HEALTH)


def on_turn_start_swan(pet: Pet, team: Team, shop: Shop):
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
        rat_spawn = get_base_pet(Species.PET_SPAWN).set_stats(attack=1, health=1)

        # the rat always try to spawn it up front for the opponent
        front_idx = len(enemy_pets) - 1

        try_spawn_at_pos(
            rat_spawn, idx=front_idx, pets=enemy_pets, is_in_battle=is_in_battle
        )


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
                receiving_pet=my_pet,
                attacking_pet=pet,
                damage=damage,
                receiving_team=my_pets,
                opposing_team=enemy_pets,
                is_in_battle=is_in_battle,
            )

    if enemy_pets is None:
        return

    for enemy_pet in enemy_pets:
        receive_damage(
            receiving_pet=enemy_pet,
            attacking_pet=pet,
            damage=damage,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            is_in_battle=is_in_battle,
        )


def on_hurt_peacock(
    pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet], is_in_battle: bool
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
    closest_friends_behind = get_nearest_friends_behind_idx(
        behind_idx=faint_pet_idx, my_pets=my_pets, num_friends=2
    )

    stat_boost = pet.get_level()
    for friend in closest_friends_behind:
        friend.add_stats(attack=stat_boost, health=stat_boost)


def on_turn_start_worm(pet: Pet, team: Team, shop: Shop):
    # the apple the worm stocks is an ADDITIONAL food (doesn't take up a food slot)
    # https://youtu.be/T6moXKCurxw?si=HA5rgHUkSFPiPjh1&t=147

    cost_discount = 0
    match pet.get_level():
        case 1:
            apple_kind = Food.APPLE
            cost_discount = 1
        case 2:
            apple_kind = Food.APPLE_2_COST_BETTER
        case 3:
            apple_kind = Food.APPLE_2_COST_BEST

    food_to_add = FoodShopSlot(apple_kind)
    food_to_add.cost -= cost_discount
    shop.food_slots.append(food_to_add)


def on_friend_ahead_attacks_kangaroo(
    pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]
):
    stat_buff = pet.get_level()
    pet.add_stats(attack=stat_buff, health=stat_buff)


def on_faint_spider(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    pet_to_spawn = random.choice(tier_3_pets).clone()
    stat = 2 * pet.get_level()

    # we need to ensure that the new pet has the proper experience since if it's spawned in the shop, it should have the proper experience
    new_spawn_experience = get_experience_for_level(pet.get_level())

    pet_to_spawn.set_stats_all(
        attack=stat,
        health=stat,
        effect=Effect.NONE,
        experience=new_spawn_experience,
        attack_boost=0,
        health_boost=0,
    )
    try_spawn_at_pos(pet_to_spawn, faint_pet_idx, my_pets, is_in_battle)


def on_battle_start_dodo(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    # the dodo's attack is NOT cleared from it's own. it buffs the friend's attack https://youtu.be/7zymvXc9OrU?si=KVVqzWX1u6-z_LCc&t=76
    percentage_amount_to_give = 0.5 * pet.get_level()

    # use ceil. so if the dodo has 1 attack, we give 1 attack to the friend
    attack_to_give_to_friend = math.ceil(percentage_amount_to_give * pet.attack)

    nearest_friends_ahead = get_nearest_friends_ahead(pet, my_pets, num_friends=1)
    if len(nearest_friends_ahead) == 0:
        return

    nearest_friends_ahead[0].add_stats(attack=attack_to_give_to_friend)


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
                receiving_pet=pet_ahead,
                attacking_pet=pet,
                damage=damage_to_deal,
                receiving_team=my_pets,
                opposing_team=enemy_pets,
                is_in_battle=is_in_battle,
            )
    else:  # else: the badger is at the front of the team
        if is_in_battle and len(enemy_pets) > 0:
            pet_ahead = enemy_pets[-1]
            receive_damage(
                receiving_pet=pet_ahead,
                attacking_pet=pet,
                damage=damage_to_deal,
                receiving_team=enemy_pets,
                opposing_team=my_pets,
                is_in_battle=is_in_battle,
            )
        # else: there is no pet ahead to deal damage to

    # now deal damage to the pet behind (you can only damage your own team)
    if faint_pet_idx > 0:
        pet_behind = my_pets[faint_pet_idx - 1]
        receive_damage(
            receiving_pet=pet_behind,
            attacking_pet=pet,
            damage=damage_to_deal,
            receiving_team=my_pets,
            opposing_team=enemy_pets,
            is_in_battle=is_in_battle,
        )


# does the dolphin trigger onto on one pet or multiple pets? I think it can trigger to multiple pets
def on_battle_start_dolphin(
    pet: Pet,
    my_pets: list[Pet],
    enemy_pets: list[Pet],
):
    num_triggers = pet.get_level()
    for _ in range(num_triggers):
        lowest_health_enemy_pet = get_pet_with_lowest_health(enemy_pets)

        if lowest_health_enemy_pet is None:
            return

        # now deal damage to the lowest health enemy pet
        receive_damage(
            receiving_pet=lowest_health_enemy_pet,
            attacking_pet=pet,
            damage=4,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            is_in_battle=True,
        )


def on_turn_start_giraffe(pet: Pet, team: Team, shop: Shop):
    nearest_friends_ahead = get_nearest_friends_ahead(
        pet, my_pets=team.pets, num_friends=pet.get_level()
    )
    for friend in nearest_friends_ahead:
        friend.add_stats(attack=1, health=1)


def on_after_attack_elephant(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    nearest_friends_behind = get_nearest_friends_behind(pet, my_pets, num_friends=1)
    if len(nearest_friends_behind) == 1:
        num_triggers = pet.get_level()
        for _ in range(num_triggers):
            receive_damage(
                receiving_pet=nearest_friends_behind[0],
                attacking_pet=pet,
                damage=1,
                receiving_team=my_pets,
                opposing_team=enemy_pets,
                is_in_battle=True,
            )


def on_hurt_camel(
    pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet], is_in_battle: bool
):
    nearest_friends_behind = get_nearest_friends_behind(pet, my_pets, num_friends=1)
    if len(nearest_friends_behind) == 1:
        nearest_friend = nearest_friends_behind[0]
        nearest_friend.add_stats(attack=pet.get_level(), health=2 * pet.get_level())


def on_friendly_ate_food_rabbit(pet: Pet, pet_that_ate_food: Pet, team: Team):
    if pet.metadata["num_friendlies_buffed"] < 4:
        pet.metadata["num_friendlies_buffed"] += 1
        pet_that_ate_food.add_stats(health=pet.get_level())


def on_friend_ahead_faints_ox(pet: Pet, my_pets: list[Pet], is_in_battle: bool):
    # I'm assuming the melon buff will override any existing buff the ox has
    if pet.metadata["num_times_buff_itself"] < pet.get_level():
        pet.metadata["num_times_buff_itself"] += 1
        pet.effect = Effect.MELON
        pet.add_stats(attack=1)


def on_friend_summoned_dog(
    pet: Pet, summoned_friend: Pet, my_pets: list[Pet], is_in_battle: bool
):
    pet_level = pet.get_level()
    attack_buff = 2 * pet_level
    health_buff = pet_level
    if is_in_battle:
        pet.add_stats(attack=attack_buff, health=health_buff)
    else:
        pet.add_boost(attack=attack_buff, health=health_buff)


def on_faint_sheep(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    num_triggers = 2
    for _ in range(num_triggers):
        ram_stats = 2 * pet.get_level()
        ram_to_summon = get_base_pet(Species.PET_SPAWN).set_stats(
            attack=ram_stats, health=ram_stats
        )
        try_spawn_at_pos(ram_to_summon, faint_pet_idx, my_pets, is_in_battle)


def on_battle_start_skunk(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    highest_health_enemy_pet = get_pet_with_highest_health(enemy_pets)
    match pet.get_level():
        case 1:
            health_percentage_to_remove = 0.33
        case 2:
            health_percentage_to_remove = 0.66
        case 3:
            health_percentage_to_remove = 0.99
    highest_health_enemy_pet.health = math.ceil(
        highest_health_enemy_pet.health * health_percentage_to_remove
    )


def on_knock_out_hippo(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    if pet.metadata["num_times_buffed"] < 3:
        pet.metadata["num_times_buffed"] += 1
        stat_buff = 3 * pet.get_level()
        pet.add_stats(attack=stat_buff, health=stat_buff)


def on_end_turn_bison(pet: Pet, team: Team, last_battle_result: BattleResult):
    for my_pet in team.pets:
        if my_pet is not pet and my_pet.get_level() == 3:
            attack_buff = my_pet.get_level()
            health_buff = 2 * my_pet.get_level()
            my_pet.add_stats(attack=attack_buff, health=health_buff)
            return  # bison only buffs itself once


def on_hurt_blowfish(
    pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet], is_in_battle: bool
):
    damage_to_deal = 3 * pet.get_level()
    enemy_pet = Team.get_random_pets_from_list(enemy_pets, select_num_pets=1)[0]
    receive_damage(
        receiving_pet=enemy_pet,
        attacking_pet=pet,
        damage=damage_to_deal,
        receiving_team=enemy_pets,
        opposing_team=my_pets,
        is_in_battle=is_in_battle,
    )


def on_faint_turtle(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    nearest_friends = get_nearest_friends_behind_idx(
        behind_idx=faint_pet_idx, my_pets=my_pets, num_friends=pet.get_level()
    )
    for friend in nearest_friends:
        friend.effect = Effect.MELON


def on_turn_start_squirrel(pet: Pet, team: Team, shop: Shop):
    discount_amount = pet.get_level()
    for food_slot in shop.food_slots:
        food_slot.cost = max(food_slot.cost - discount_amount, 0)


def on_end_turn_penguin(pet: Pet, team: Team, last_battle_result: BattleResult):
    # penguins do NOT buff themselves
    pets_that_are_level_2_or_3 = [
        my_pet for my_pet in team.pets if my_pet.get_level() >= 2
    ]

    buff_amount = pet.get_level()
    for target_pet in Team.get_random_pets_from_list(
        pets_that_are_level_2_or_3, select_num_pets=2, exclude_pet=pet
    ):
        target_pet.add_stats(attack=buff_amount, health=buff_amount)


def on_faint_deer(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    bus = get_base_pet(Species.PET_SPAWN)
    bus.effect = Effect.CHILLI
    attack_buff = 5 * pet.get_level()
    health_buff = 3 * pet.get_level()
    bus.add_stats(attack=attack_buff, health=health_buff)
    try_spawn_at_pos(bus, faint_pet_idx, my_pets, is_in_battle)


def on_battle_start_whale(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    # They are also considered "new" pets, with no memory of their old selves before being swallowed.
    # https://superautopets.fandom.com/wiki/Whale
    for friend in get_nearest_friends_ahead(pet, my_pets, num_friends=1):
        pet.metadata["on_faint_spawn_species_kind"] = friend.species.value
        # swallow the friend:
        make_pet_faint(pet, my_pets=my_pets, enemy_pets=enemy_pets, is_in_battle=True)


def on_faint_whale(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    # from the wiki: Summoned friend's stats will be their base stats multiplied by the Whale’s level.
    species_to_spawn = Species(pet.metadata["on_faint_spawn_species_kind"])
    new_pet = get_base_pet(species_to_spawn)
    new_pet.experience = get_experience_for_level(pet.get_level())
    new_pet.set_stats(
        attack=new_pet.attack * pet.get_level(), health=new_pet.health * pet.get_level()
    )
    try_spawn_at_pos(new_pet, faint_pet_idx, my_pets, is_in_battle)


def on_end_turn_parrot(pet: Pet, team: Team, last_battle_result: BattleResult):
    for friend in get_nearest_friends_ahead(pet, team.pets, num_friends=1):
        # make the parrot's data fresh for the next copy
        pet.metadata.clear()
        pet.clear_triggers()

        pet.copy_triggers(friend)
        # we don't need to run the trigger (if it's an on end turn trigger). since the copied triggers will be run on order of append

        # re-add the parrot triggers
        pet.set_trigger(Trigger.ON_END_TURN, on_end_turn_parrot)
        pet.set_trigger(Trigger.ON_TURN_START, clear_metadata)


def on_battle_start_crocodile(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    # assuming the crocodile can hit multiple enemies "Basically means that crocodile can now hit multiple units"
    # https://www.reddit.com/r/superautopets/comments/ut58i3/turns_out_new_crocodile_is_pretty_good/?rdt=43846
    num_triggers = pet.get_level()
    for _ in range(num_triggers):
        if len(enemy_pets) == 0:
            return
        last_enemy = enemy_pets[0]
        receive_damage(
            receiving_pet=last_enemy,
            attacking_pet=pet,
            damage=8,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            is_in_battle=True,
        )


def on_knock_out_rhino(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    if len(enemy_pets) == 0:
        return

    first_enemy = enemy_pets[-1]
    damage_to_deal = 4 * pet.get_level()

    if first_enemy.species in tier_1_pet_species:
        damage_to_deal = damage_to_deal * 2

    receive_damage(
        receiving_pet=first_enemy,
        attacking_pet=pet,
        damage=damage_to_deal,
        receiving_team=enemy_pets,
        opposing_team=my_pets,
        is_in_battle=True,
    )


# does the monkey boost itself? I think it can. cause the desc says "friendly"
def on_end_turn_monkey(pet: Pet, team: Team, last_battle_result: BattleResult):
    stat_buff = 2 * pet.get_level()

    # we cannot use team.pets[-1] since it might be a none pet
    # note: this list is never empty since the monkey is on the team
    frontmost_pet = team.get_no_none_pets()[-1]
    frontmost_pet.add_stats(attack=stat_buff, health=stat_buff)


def on_battle_start_armadillo(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    health_buff = 8 * pet.get_level()
    for pet in my_pets:
        pet.add_stats(health=health_buff)
    for pet in enemy_pets:
        pet.add_stats(health=health_buff)


def on_buy_cow(pet: Pet, team: Team, shop: Shop):
    match pet.get_level():
        case 1:
            milk_type = Food.MILK
        case 2:
            milk_type = Food.BETTER_MILK
        case 3:
            milk_type = Food.BEST_MILK
    shop.food_slots = []
    for _ in range(2):
        shop.food_slots.append(FoodShopSlot(milk_type))


def on_friendly_ate_food_seal(pet: Pet, pet_that_ate_food: Pet, team: Team):
    if pet_that_ate_food is not pet:
        return
    attack_buff = pet.get_level()
    # pretty sure we exclude itself since it says "friends", not "friendly"
    for pet in team.get_random_pets(3, exclude_pet=pet):
        pet.add_stats(attack=attack_buff)


def on_faint_rooster(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    num_triggers = pet.get_level()
    for _ in range(num_triggers):
        chick_spawn = get_base_pet(Species.PET_SPAWN).set_stats(
            health=1, attack=math.ceil(pet.attack / 2)
        )
        try_spawn_at_pos(chick_spawn, faint_pet_idx, my_pets, is_in_battle)


def on_friend_faints_shark(
    pet: Pet, faint_pet_idx: int, my_pets: list[Pet], is_in_battle: bool
):
    stat_buff = 2 * pet.get_level()
    pet.add_stats(attack=stat_buff, health=stat_buff)


def on_friend_summoned_turkey(
    pet: Pet, summoned_friend: Pet, my_pets: list[Pet], is_in_battle: bool
):
    attack_boost = 3 * pet.get_level()
    health_boost = pet.get_level()
    # yes. these stats are permanent
    pet.add_stats(attack=attack_boost, health=health_boost)


def on_battle_start_leopard(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    damage = math.ceil(0.5 * pet.attack)
    for enemy_pet in Team.get_random_pets_from_list(
        enemy_pets, select_num_pets=pet.get_level()
    ):
        receive_damage(
            receiving_pet=enemy_pet,
            attacking_pet=pet,
            damage=damage,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            is_in_battle=True,
        )


def on_before_attack_boar(pet: Pet):
    attack_buff = 4 * pet.get_level()
    health_buff = 2 * pet.get_level()
    pet.add_stats(attack=attack_buff, health=health_buff)


# Tiger considerations
# - triggers should pass in the level so we know what level to do abilities on
#     - mayb instead we set the metadata of hte pet and the get_level() function can be overriden for tiger triggers?
# - what triggers should NOT be triggered more than once? (those htat set metadata?)
# - does the tiger go past trigger caps ? like will the rabbit be able to buff 2x as many pets?
#    - "Friends repeating their abilities won't deplete additional triggers" https://superautopets.fandom.com/wiki/Tiger
#    - "or certain abilities like Crab or Butterfly, a low level Tiger will make them perform their copy abilities again at lower level, and end up copying less stats."


# https://www.youtube.com/clip/UgkxRYjQsIKoqkXkyBtE76ULs7hcYJ6fG1-n
def on_friend_hurt_wolverine(
    pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet], is_in_battle: bool
):
    pet.metadata["num_times_hurt"] = (pet.metadata["num_times_hurt"] + 1) % 4
    # it reduces the health up to 1. it ignores garlic
    health_reduction = 3 * pet.get_level()
    for enemy_pet in enemy_pets:
        enemy_pet.health = max(enemy_pet.health - health_reduction, 1)


def on_hurt_gorilla(
    pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet], is_in_battle: bool
):
    pet.metadata["num_times_hurt"] += 1
    if pet.metadata["num_times_hurt"] <= pet.get_level():
        pet.effect = Effect.MELON


def on_friend_bought_dragon(pet: Pet, bought_pet: Pet, team: Team):
    if bought_pet.species not in tier_1_pet_species:
        return

    stat_buff = pet.get_level()
    for team_pet in team.pets:
        # the dragon does not buff itself https://youtu.be/IfOVDc7g3W4?si=esEDFcEEj-nWbD19&t=376
        if team_pet is not pet:
            pet.add_stats(attack=stat_buff, health=stat_buff)


def on_faint_mammoth(
    pet: Pet,
    faint_pet_idx: int,
    my_pets: list[Pet],
    enemy_pets: list[Pet] | None,
    is_in_battle: bool,
):
    stat_buff = 2 * pet.get_level()
    for my_pet in my_pets:
        if my_pet is not pet:
            my_pet.add_stats(attack=stat_buff, health=stat_buff)


def on_friend_ahead_attacks_snake(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    damage = 5 * pet.get_level()
    for enemy_pet in Team.get_random_pets_from_list(enemy_pets, select_num_pets=1):
        receive_damage(
            receiving_pet=enemy_pet,
            attacking_pet=pet,
            damage=damage,
            receiving_team=enemy_pets,
            opposing_team=my_pets,
            is_in_battle=True,
        )


def on_friend_faints_fly(
    pet: Pet, faint_pet_idx: int, my_pets: list[Pet], is_in_battle: bool
):
    if pet.metadata["num_zombie_flies_spawned"] < 3:
        fainted_pet = my_pets[faint_pet_idx]
        if fainted_pet.metadata["is_zombie_fly"]:
            # we do not spawn a fly if the pet was a zombie fly
            return
        pet.metadata["num_zombie_flies_spawned"] += 1
        spawn_stats = 4 * pet.get_level()
        fly_spawn = get_base_pet(Species.PET_SPAWN).set_stats(
            attack=spawn_stats, health=spawn_stats
        )
        fly_spawn.metadata["is_zombie_fly"] = 1
        try_spawn_at_pos(fly_spawn, faint_pet_idx, my_pets, is_in_battle)


def set_pet_triggers():
    # disable formatting so the trigger definitions are declared on one line
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
    species_to_pet_map[Species.GIRAFFE].set_trigger(Trigger.ON_TURN_START, on_turn_start_giraffe)
    species_to_pet_map[Species.ELEPHANT].set_trigger(Trigger.ON_AFTER_ATTACK, on_after_attack_elephant)
    species_to_pet_map[Species.CAMEL].set_trigger(Trigger.ON_HURT, on_hurt_camel)
    species_to_pet_map[Species.RABBIT].set_trigger(Trigger.ON_FRIENDLY_ATE_FOOD, on_friendly_ate_food_rabbit)
    species_to_pet_map[Species.RABBIT].set_trigger(Trigger.ON_END_TURN, clear_metadata) # reset the rabbit's limit on buffing friendly
    species_to_pet_map[Species.OX].set_trigger(Trigger.ON_FRIEND_AHEAD_FAINTS, on_friend_ahead_faints_ox)
    species_to_pet_map[Species.OX].set_trigger(Trigger.ON_END_TURN, clear_metadata) # reset the ox's limit on buffing itself
    species_to_pet_map[Species.DOG].set_trigger(Trigger.ON_FRIEND_SUMMONED, on_friend_summoned_dog)
    species_to_pet_map[Species.SHEEP].set_trigger(Trigger.ON_FAINT, on_faint_sheep)

    # tier 4
    species_to_pet_map[Species.SKUNK].set_trigger(Trigger.ON_BATTLE_START, on_battle_start_skunk)
    species_to_pet_map[Species.HIPPO].set_trigger(Trigger.ON_KNOCK_OUT, on_knock_out_hippo)
    species_to_pet_map[Species.HIPPO].set_trigger(Trigger.ON_BATTLE_START, clear_metadata) # reset the hippo's knock out
    species_to_pet_map[Species.BISON].set_trigger(Trigger.ON_END_TURN, on_end_turn_bison)
    species_to_pet_map[Species.BLOWFISH].set_trigger(Trigger.ON_HURT, on_hurt_blowfish)
    species_to_pet_map[Species.TURTLE].set_trigger(Trigger.ON_FAINT, on_faint_turtle)
    species_to_pet_map[Species.SQUIRREL].set_trigger(Trigger.ON_TURN_START, on_turn_start_squirrel)
    species_to_pet_map[Species.PENGUIN].set_trigger(Trigger.ON_END_TURN, on_end_turn_penguin)
    species_to_pet_map[Species.DEER].set_trigger(Trigger.ON_FAINT, on_faint_deer)
    species_to_pet_map[Species.WHALE].set_trigger(Trigger.ON_BATTLE_START, on_battle_start_whale)
    species_to_pet_map[Species.WHALE].set_trigger(Trigger.ON_FAINT, on_faint_whale)
    species_to_pet_map[Species.WHALE].set_trigger(Trigger.ON_TURN_START, clear_metadata) # reset the whale's spawn (so pills don't repawn it in the shop - I think thisi s hte intended ehaviour. haven't tested)
    species_to_pet_map[Species.PARROT].set_trigger(Trigger.ON_END_TURN, on_end_turn_parrot)

    # tier 5
    # scorpion has no triggers. it just inately has the peanut effect
    species_to_pet_map[Species.CROCODILE].set_trigger(Trigger.ON_BATTLE_START, on_battle_start_crocodile)
    species_to_pet_map[Species.RHINO].set_trigger(Trigger.ON_KNOCK_OUT, on_knock_out_rhino)
    species_to_pet_map[Species.MONKEY].set_trigger(Trigger.ON_END_TURN, on_end_turn_monkey)
    species_to_pet_map[Species.ARMADILLO].set_trigger(Trigger.ON_BATTLE_START, on_battle_start_armadillo)
    species_to_pet_map[Species.COW].set_trigger(Trigger.ON_BUY, on_buy_cow)
    species_to_pet_map[Species.SEAL].set_trigger(Trigger.ON_FRIENDLY_ATE_FOOD, on_friendly_ate_food_seal)
    species_to_pet_map[Species.ROOSTER].set_trigger(Trigger.ON_FAINT, on_faint_rooster)
    species_to_pet_map[Species.SHARK].set_trigger(Trigger.ON_FRIEND_FAINTS, on_friend_faints_shark)
    species_to_pet_map[Species.TURKEY].set_trigger(Trigger.ON_FRIEND_SUMMONED, on_friend_summoned_turkey)

    # tier 6
    species_to_pet_map[Species.LEOPARD].set_trigger(Trigger.ON_BATTLE_START, on_battle_start_leopard)
    species_to_pet_map[Species.BOAR].set_trigger(Trigger.ON_BEFORE_ATTACK, on_before_attack_boar)
    # tiger's triggers are deal inside the pet's trigger function (so it can dupliate the effect)
    species_to_pet_map[Species.WOLVERINE].set_trigger(Trigger.ON_FRIEND_HURT, on_friend_hurt_wolverine)
    species_to_pet_map[Species.GORILLA].set_trigger(Trigger.ON_HURT, on_hurt_gorilla)
    species_to_pet_map[Species.GORILLA].set_trigger(Trigger.ON_TURN_START, clear_metadata)
    species_to_pet_map[Species.DRAGON].set_trigger(Trigger.ON_FRIEND_BOUGHT, on_friend_bought_dragon)
    species_to_pet_map[Species.MAMMOTH].set_trigger(Trigger.ON_FAINT, on_faint_mammoth)
    species_to_pet_map[Species.CAT].set_trigger(Trigger.ON_TURN_START, clear_metadata)
    species_to_pet_map[Species.SNAKE].set_trigger(Trigger.ON_FRIEND_AHEAD_ATTACKS, on_friend_ahead_attacks_snake)
    species_to_pet_map[Species.FLY].set_trigger(Trigger.ON_FRIEND_FAINTS, on_friend_faints_fly)
    species_to_pet_map[Species.FLY].set_trigger(Trigger.ON_TURN_START, clear_metadata)

    # fmt: on


def clear_metadata(pet: Pet, *args: Any, **kwargs: Any):
    pet.metadata.clear()


class CallableProtocol(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


# Validate at runtime that all the triggers follow the correct interface
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

    # Check if the function signature strictly matches the protocol's signature
    if func_signature == protocol_signature:
        return

    # Check if the function is universal (works with any trigger) (has Pet, *args and, **kwargs)
    func_param_values = list(func_signature.parameters.values())
    is_universally_accepted_by_all_triggers = (
        len(func_param_values) == 3
        and func_param_values[0].name == "pet"
        and func_param_values[1].kind == inspect.Parameter.VAR_POSITIONAL
        and func_param_values[2].kind == inspect.Parameter.VAR_KEYWORD
    )

    if not is_universally_accepted_by_all_triggers:
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
    Trigger.ON_AFTER_ATTACK: OnAfterAttack,
    Trigger.ON_FRIENDLY_ATE_FOOD: OnFriendlyAteFood,
    Trigger.ON_FRIEND_AHEAD_FAINTS: OnFriendAheadFaints,
    Trigger.ON_KNOCK_OUT: OnKnockOut,
    Trigger.ON_FRIEND_FAINTS: OnFriendFaints,
    Trigger.ON_BEFORE_ATTACK: OnBeforeAttack,
    Trigger.ON_FRIEND_HURT: OnFriendHurt,
    Trigger.ON_FRIEND_BOUGHT: OnFriendBought,
}


def validate_trigger_protocols():
    for pet in species_to_pet_map.values():
        for trigger, trigger_fns in pet._triggers.items():
            for trigger_fn in trigger_fns:
                protocol_type = trigger_to_protocol_type[trigger]
                validate_protocol(trigger_fn, protocol_type)


def validate_can_trigger_in_shop_or_battle_triggers_have_is_in_battle_kwarg():
    """
    Ensures that every trigger in `can_trigger_in_shop_or_battle`
    requires an `is_in_battle` parameter in its protocol signature.
    """
    for trigger in can_trigger_in_shop_or_battle:
        protocol_cls = trigger_to_protocol_type[trigger]
        # Get the signature of the protocol's __call__ method
        sig = inspect.signature(protocol_cls.__call__)

        if "is_in_battle" not in sig.parameters:
            raise TypeError(
                f"Trigger type {trigger} must have an 'is_in_battle' parameter as it can trigger in both the shop and battle. (needed for the tiger to know if it should trigger)"
            )
        if "my_pets" not in sig.parameters and "team" not in sig.parameters:
            raise TypeError(
                f"Trigger type {trigger} must have a 'my_pets' or 'team' parameter as it can trigger in both the shop and battle. (needed for the tiger to know which pets are in the team)"
            )
