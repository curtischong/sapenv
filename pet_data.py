from all_types_and_consts import ShopTier, Species
from pet import Pet


tier_1_pets: list[Pet] = [
    Pet.define_base_stats(
        species=Species.DUCK,
        attack=2,
        health=1,
    ),
    Pet.define_base_stats(
        species=Species.BEAVER,
        attack=2,
        health=1,
    ),
    Pet.define_base_stats(
        species=Species.PIGEON,
        attack=3,
        health=1,
    ),
    Pet.define_base_stats(
        species=Species.NONE,
        attack=-1,
        health=-1,
    ),
]
tier_2_pets: list[Pet] = [
    Pet.define_base_stats(
        species=Species.DUCK,
        attack=2,
        health=1,
    ),
    Pet.define_base_stats(
        species=Species.BEAVER,
        attack=2,
        health=1,
    ),
    Pet.define_base_stats(
        species=Species.PIGEON,
        attack=3,
        health=1,
    ),
    Pet.define_base_stats(
        species=Species.NONE,
        attack=-1,
        health=-1,
    ),
]

all_pets: list[Pet] = tier_1_pets
assert len(all_pets) == len(Species)

species_to_pet_map: dict[Species, Pet] = {pet.species: pet for pet in all_pets}
shop_tier_to_pets_map: dict[ShopTier, list[Pet]] = {
    1: tier_1_pets,
    2: tier_2_pets,
    3: tier_3_pets,
    4: tier_4_pets,
    5: tier_5_pets,
    6: tier_6_pets,
}


def get_base_pet(species: Species):
    return species_to_pet_map[species].clone()
