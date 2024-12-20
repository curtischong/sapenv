from all_types_and_consts import Species
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

all_pets: list[Pet] = tier_1_pets
# assert len(all_pets) == len(Species) # TODO: enable this assertion

species_to_pet_map: dict[Species, Pet] = {pet.species: pet for pet in all_pets}


def get_base_pet(species: Species):
    return species_to_pet_map[species].clone()
