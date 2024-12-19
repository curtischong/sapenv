from all_types_and_consts import Species
from pet import Pet


tier_1_pets = [
    Pet.define_base_stats(
        species=Species.DUCK,
        health=2,
        defence=1,
    ),
    Pet.define_base_stats(
        species=Species.BEAVER,
        health=2,
        defence=1,
    ),
    Pet.define_base_stats(
        species=Species.PIGEON,
        health=3,
        defence=1,
    ),
]
