from all_types_and_consts import BattleResult, Effect, Food, Species, Trigger
from battle import receive_damage, try_spawn_at_pos
from pet import Pet
from shop import Shop
from team import Team
from pet_data import get_base_pet, species_to_pet_map


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


def on_faint_ant(pet: Pet, team_pets: list[Pet], is_in_battle: bool):
    pet_list = Team.get_random_pets_from_list(
        team_pets=team_pets, select_num_pets=1, exclude_pet=pet
    )
    if len(pet_list) > 0:
        stat_buff = pet.get_level()
        pet_list[0].add_stats(attack=stat_buff, health=stat_buff)


def on_battle_start_mosquito(pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]):
    random_pets = Team.get_random_pets(select_num_pets=pet.get_level())
    for enemy_pet, idx in random_pets:
        receive_damage(
            pet=enemy_pet,
            damage=1,
            team_pets=enemy_pets,
            attacker_has_peanut_effect=pet.effect == Effect.PEANUT,
        )


# this is called AFTER they level up
def on_level_up_fish(pet: Pet, team: Team):
    pet_level = pet.get_level()
    assert pet_level > 1
    stat_buff = pet_level - 1
    for pet in team.get_random_pets(2, exclude_pet=pet):
        pet.add_stats(attack=stat_buff, health=stat_buff)


def on_faint_cricket(pet: Pet, team_pets: list[Pet], is_in_battle: bool):
    pet_idx = team_pets.index(pet)
    cricket_spawn = get_base_pet(Species.CRICKET_SPAWN).set_stats(
        attack=pet.get_level(), health=pet.get_level()
    )
    try_spawn_at_pos(cricket_spawn, pet_idx, team_pets, is_in_battle=is_in_battle)


def on_friend_summoned_horse(pet: Pet, summoned_friend: Pet, is_in_battle: bool):
    assert pet is not summoned_friend
    attack_boost = pet.get_level()
    if is_in_battle:
        # if in battle, add stats instead of boost
        summoned_friend.add_stats(attack=attack_boost, health=0)
    else:
        summoned_friend.add_boost(attack=attack_boost, health=0)


def on_end_turn_snail(pet: Pet, team: Team, last_battle_result: BattleResult):
    # https://superautopets.fandom.com/wiki/Snail
    # it only triggers if it's a loss, not a draw
    # If Snail is bought on turn 1, the "last battle" will be considered a draw.
    # the snail does not buff itself: https://youtu.be/jk9z6yPkG3U?si=1Cwf11gtm4wgpaMr&t=451
    if last_battle_result != BattleResult.LOST_BATTLE:
        return

    buff_amount = pet.get_level()
    for team_pet in team.pets:
        if team_pet is not pet:
            team_pet.add_stats(attack=buff_amount, health=buff_amount)


def set_pet_triggers():
    # tier 1
    species_to_pet_map[Species.DUCK].set_trigger(Trigger.ON_SELL, on_sell_duck)
    species_to_pet_map[Species.BEAVER].set_trigger(Trigger.ON_SELL, on_sell_beaver)
    species_to_pet_map[Species.PIGEON].set_trigger(Trigger.ON_SELL, on_sell_pigeon)
    species_to_pet_map[Species.OTTER].set_trigger(Trigger.ON_BUY, on_buy_otter)
    species_to_pet_map[Species.PIG].set_trigger(Trigger.ON_SELL, on_sell_pig)
    species_to_pet_map[Species.ANT].set_trigger(Trigger.ON_FAINT, on_faint_ant)
    species_to_pet_map[Species.MOSQUITO].set_trigger(
        Trigger.ON_BATTLE_START, on_battle_start_mosquito
    )
    species_to_pet_map[Species.FISH].set_trigger(Trigger.ON_LEVEL_UP, on_level_up_fish)
    species_to_pet_map[Species.CRICKET].set_trigger(Trigger.ON_FAINT, on_faint_cricket)
    species_to_pet_map[Species.HORSE].set_trigger(
        Trigger.ON_FRIEND_SUMMONED, on_friend_summoned_horse
    )
    species_to_pet_map[Species.SNAIL].set_trigger(
        Trigger.ON_END_TURN, on_end_turn_snail
    )
