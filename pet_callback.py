from pet_callback_consts import PetLevel
from shop import Shop
from team import Team


def on_sell_duck(pet_level: PetLevel, shop: Shop, team: Team):
    for slot in shop.slots:
        slot.pet.add_stats(health=pet_level)


def on_sell_beaver(pet_level: PetLevel, shop: Shop, team: Team):
    two_random_friends = team.get_random_pets(2)
    for pet in two_random_friends:
        pet.add_stats(attack=pet_level)
