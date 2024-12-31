from all_types_and_consts import Species
from pet import Pet


def get_nearest_friends_ahead(
    pet: Pet, my_pets: list[Pet], num_friends: int
) -> list[Pet]:
    pet_idx = my_pets.index(pet)
    friend_idx = pet_idx + 1
    friends_ahead = []

    while len(friends_ahead) < num_friends and friend_idx < len(my_pets):
        friend_pet = my_pets[friend_idx]
        if friend_pet.species != Species.NONE:
            friends_ahead.append(friend_pet)
        friend_idx += 1

    return friends_ahead


def get_nearest_friends_behind(
    pet: Pet, my_pets: list[Pet], num_friends: int
) -> list[Pet]:
    pet_idx = my_pets.index(pet)
    friend_idx = pet_idx - 1
    friends_behind = []

    while len(friends_behind) < num_friends and friend_idx >= 0:
        friend_pet = my_pets[friend_idx]
        if friend_pet.species != Species.NONE:
            friends_behind.append(friend_pet)
        friend_idx -= 1

    return friends_behind


def get_pet_with_highest_health(pets: list[Pet]) -> Pet:
    max_health_on_team = 0
    target_pet = None
    for pet in pets:
        if pet.health > max_health_on_team:
            max_health_on_team = pet.health
            target_pet = pet
    return target_pet
