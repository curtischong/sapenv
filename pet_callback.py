from all_types_and_consts import Effect, Food, Species
from battle import receive_damage
from pet import Pet
from pet_callback_consts import PetLevel
from shop import Shop
from team import Team
from pet_data import species_to_pet_map


def on_sell_duck(pet_level: PetLevel, shop: Shop, team: Team):
    for slot in shop.slots:
        slot.pet.add_stats(health=pet_level)


def on_sell_beaver(pet_level: PetLevel, shop: Shop, team: Team):
    two_random_friends = team.get_random_pets(2)
    for pet in two_random_friends:
        pet.add_stats(attack=pet_level)


def on_sell_pigeon(pet_level: PetLevel, shop: Shop, team: Team):
    shop.num_foods[Food.BREAD_CRUMB] += 1


def on_buy_otter(pet_level: PetLevel, shop: Shop, team: Team):
    random_friends = team.get_random_pets(pet_level)
    for pet in random_friends:
        pet.add_stats(health=1)


def on_sell_pig(pet_level: PetLevel, shop: Shop, team: Team):
    shop.gold += pet_level


def on_faint_ant(pet_level: PetLevel, shop: Shop, team: Team):
    pet_list = team.get_random_pets(1)
    if len(pet_list) > 0:
        pet_list[0].add_stats(attack=pet_level, health=pet_level)


def on_battle_start(
    pet: Pet, pet_level: PetLevel, my_pets: list[Pet], enemy_pets: list[Pet]
):
    pets_with_idxs = Team.get_random_pets_with_idxs(
        pets_list=enemy_pets, select_num_pets=pet_level
    )
    for enemy_pet, idx in pets_with_idxs:
        receive_damage(
            pet=enemy_pet,
            damage=1,
            idx_in_team=idx,
            team_pets=enemy_pets,
            attacker_has_peanut_effect=pet.effect == Effect.PEANUT,
        )


def set_pet_callbacks():
    # tier 1
    species_to_pet_map[Species.DUCK].set_on_sell(on_sell_duck)
    species_to_pet_map[Species.BEAVER].set_on_sell(on_sell_beaver)
    species_to_pet_map[Species.PIGEON].set_on_sell(on_sell_pigeon)
    species_to_pet_map[Species.OTTER].set_on_buy(on_buy_otter)
    species_to_pet_map[Species.PIG].set_on_sell(on_sell_pig)
    species_to_pet_map[Species.ANT].set_on_faint(on_faint_ant)
    species_to_pet_map[Species.MOSQUITO].set_on_battle_start(on_battle_start)
