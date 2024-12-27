from all_types_and_consts import Species
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
    pass  # needs to implement food


def on_buy_otter(pet_level: PetLevel, shop: Shop, team: Team):
    random_friends = team.get_random_pets(pet_level)
    for pet in random_friends:
        pet.add_stats(health=1)


def set_pet_callbacks():
    species_to_pet_map[Species.DUCK].set_on_sell(on_sell_duck)
    species_to_pet_map[Species.BEAVER].set_on_sell(on_sell_beaver)
    species_to_pet_map[Species.OTTER].set_on_buy(on_buy_otter)