from all_types_and_consts import Effect, Food, Species
from battle import receive_damage
from pet import Pet
from shop import Shop
from team import Team
from pet_data import species_to_pet_map


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


def on_faint_ant(pet: Pet, shop: Shop, team: Team):
    pet_list = team.get_random_pets(1, exclude_pet=pet)
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


def set_pet_callbacks():
    # tier 1
    species_to_pet_map[Species.DUCK].set_on_sell(on_sell_duck)
    species_to_pet_map[Species.BEAVER].set_on_sell(on_sell_beaver)
    species_to_pet_map[Species.PIGEON].set_on_sell(on_sell_pigeon)
    species_to_pet_map[Species.OTTER].set_on_buy(on_buy_otter)
    species_to_pet_map[Species.PIG].set_on_sell(on_sell_pig)
    species_to_pet_map[Species.ANT].set_on_faint(on_faint_ant)
    species_to_pet_map[Species.MOSQUITO].set_on_battle_start(on_battle_start_mosquito)
    species_to_pet_map[Species.FISH].set_on_level_up(on_level_up_fish)
