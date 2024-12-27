from all_types_and_consts import ShopTier, Species
from pet import Pet


tier_1_pets: list[Pet] = [
    Pet.define_base_stats(species=Species.DUCK, attack=2, health=3),
    Pet.define_base_stats(species=Species.BEAVER, attack=3, health=2),
    Pet.define_base_stats(species=Species.PIGEON, attack=3, health=1),
    Pet.define_base_stats(species=Species.OTTER, attack=1, health=3),
    Pet.define_base_stats(species=Species.PIG, attack=4, health=1),
    Pet.define_base_stats(species=Species.ANT, attack=2, health=2),
    Pet.define_base_stats(species=Species.MOSQUITO, attack=2, health=2),
    Pet.define_base_stats(species=Species.FISH, attack=2, health=3),
    Pet.define_base_stats(species=Species.CRICKET, attack=1, health=3),
    Pet.define_base_stats(species=Species.HORSE, attack=2, health=1),
]
tier_2_pets: list[Pet] = [
    Pet.define_base_stats(species=Species.SNAIL, attack=2, health=2),
    Pet.define_base_stats(species=Species.CRAB, attack=4, health=1),
    Pet.define_base_stats(species=Species.SWAN, attack=1, health=2),
    Pet.define_base_stats(species=Species.RAT, attack=3, health=6),
    Pet.define_base_stats(species=Species.HEDGEHOG, attack=4, health=2),
    Pet.define_base_stats(species=Species.PEACOCK, attack=2, health=5),
    Pet.define_base_stats(species=Species.FLAMINGO, attack=3, health=2),
    Pet.define_base_stats(species=Species.WORM, attack=1, health=3),
    Pet.define_base_stats(species=Species.KANGAROO, attack=2, health=3),
    Pet.define_base_stats(species=Species.SPIDER, attack=2, health=2),
]

tier_3_pets: list[Pet] = [
    Pet.define_base_stats(species=Species.DODO, attack=3, health=2),
    Pet.define_base_stats(species=Species.BADGER, attack=6, health=3),
    Pet.define_base_stats(species=Species.DOLPHIN, attack=4, health=3),
    Pet.define_base_stats(species=Species.GIRAFFE, attack=1, health=2),
    Pet.define_base_stats(species=Species.ELEPHANT, attack=3, health=7),
    Pet.define_base_stats(species=Species.CAMEL, attack=3, health=4),
    Pet.define_base_stats(species=Species.RABBIT, attack=1, health=2),
    Pet.define_base_stats(species=Species.OX, attack=1, health=3),
    Pet.define_base_stats(species=Species.DOG, attack=3, health=2),
    Pet.define_base_stats(species=Species.SHEEP, attack=2, health=2),
]

tier_4_pets: list[Pet] = [
    Pet.define_base_stats(species=Species.SKUNK, attack=3, health=5),
    Pet.define_base_stats(species=Species.HIPPO, attack=4, health=6),
    Pet.define_base_stats(species=Species.BISON, attack=4, health=4),
    Pet.define_base_stats(species=Species.BLOWFISH, attack=3, health=6),
    Pet.define_base_stats(species=Species.TURTLE, attack=2, health=5),
    Pet.define_base_stats(species=Species.SQUIRREL, attack=2, health=5),
    Pet.define_base_stats(species=Species.PENGUIN, attack=1, health=2),
    Pet.define_base_stats(species=Species.DEER, attack=2, health=2),
    Pet.define_base_stats(species=Species.WHALE, attack=3, health=7),
    Pet.define_base_stats(species=Species.PARROT, attack=4, health=2),
]

tier_5_pets: list[Pet] = [
    Pet.define_base_stats(species=Species.SCORPION, attack=1, health=1),
    Pet.define_base_stats(species=Species.CROCODILE, attack=8, health=4),
    Pet.define_base_stats(species=Species.RHINO, attack=6, health=7),
    Pet.define_base_stats(species=Species.MONKEY, attack=1, health=2),
    Pet.define_base_stats(species=Species.ARMADILLO, attack=2, health=10),
    Pet.define_base_stats(species=Species.COW, attack=4, health=6),
    Pet.define_base_stats(species=Species.SEAL, attack=3, health=8),
    Pet.define_base_stats(species=Species.ROOSTER, attack=6, health=4),
    Pet.define_base_stats(species=Species.SHARK, attack=2, health=2),
    Pet.define_base_stats(species=Species.TURKEY, attack=3, health=4),
]

tier_6_pets: list[Pet] = [
    Pet.define_base_stats(species=Species.LEOPARD, attack=10, health=4),
    Pet.define_base_stats(species=Species.BOAR, attack=10, health=6),
    Pet.define_base_stats(species=Species.TIGER, attack=6, health=4),
    Pet.define_base_stats(species=Species.WOLVERINE, attack=5, health=7),
    Pet.define_base_stats(species=Species.GORILLA, attack=7, health=10),
    Pet.define_base_stats(species=Species.DRAGON, attack=3, health=8),
    Pet.define_base_stats(species=Species.MAMMOTH, attack=4, health=12),
    Pet.define_base_stats(species=Species.CAT, attack=4, health=5),
    Pet.define_base_stats(species=Species.SNAKE, attack=8, health=3),
    Pet.define_base_stats(species=Species.FLY, attack=4, health=4),
]

hidden_pets: list[Pet] = [
    Pet.define_base_stats(species=Species.NONE, attack=0, health=0),
    Pet.define_base_stats(species=Species.CRICKET_SPAWN, attack=1, health=1),
    # NOTE: as the sheep levels up, these stats increase
    Pet.define_base_stats(species=Species.RAM, attack=2, health=2),
    # NOTE: as the deer levels up, these stats increase
    Pet.define_base_stats(species=Species.BUS, attack=5, health=3),
    Pet.define_base_stats(species=Species.FLY_SPAWN, attack=4, health=4),
]

all_pets: list[Pet] = (
    tier_1_pets
    + tier_2_pets
    + tier_3_pets
    + tier_4_pets
    + tier_5_pets
    + tier_6_pets
    + hidden_pets
)
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
