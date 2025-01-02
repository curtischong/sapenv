from all_types_and_consts import MAX_HEALTH, PetExperience, PetLevel, Species
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


def get_nearest_friends_behind_idx(
    behind_idx: int, my_pets: list[Pet], num_friends: int
):
    friend_idx = behind_idx - 1
    friends_behind = []

    while len(friends_behind) < num_friends and friend_idx >= 0:
        friend_pet = my_pets[friend_idx]
        if friend_pet.species != Species.NONE:
            friends_behind.append(friend_pet)
        friend_idx -= 1

    return friends_behind


def get_nearest_friends_behind(
    pet: Pet, my_pets: list[Pet], num_friends: int
) -> list[Pet]:
    pet_idx = my_pets.index(pet)
    return get_nearest_friends_behind_idx(
        behind_idx=pet_idx, my_pets=my_pets, num_friends=num_friends
    )


def get_pet_with_highest_health(pets: list[Pet]) -> Pet:
    max_health_on_team = 0
    target_pet = None
    for pet in pets:
        if pet.health > max_health_on_team:
            max_health_on_team = pet.health
            target_pet = pet
    return target_pet


def get_pet_with_lowest_health(pets: list[Pet]) -> Pet:
    lowest_health_pet = None
    lowest_health = MAX_HEALTH + 1
    for pet in pets:
        if pet.health < lowest_health:
            lowest_health_pet = pet
            lowest_health = pet.health
    return lowest_health_pet


def get_experience_for_level(level: PetLevel) -> PetExperience:
    match level:
        case 1:
            return 1
        case 2:
            return 3
        case 3:
            return 6
