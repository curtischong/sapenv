from all_types_and_consts import PetExperience, PetLevel
from pet_data import Species


class Pet:
    def __init__(
        self,
        *,
        species: str,
        attack: int,
        health: int,
        level: PetLevel,
        experience: PetExperience,
        effect: Effect | None,
    ):
        self.species = species
        self.attack = attack
        self.health = health
        self.level = level
        self.experience = experience
        self.effect = effect

    @staticmethod
    def define_base_stats(species: Species, attack: int, health: int):
        return Pet(
            species=species,
            attack=attack,
            health=health,
            level=1,
            experience=1,
            effect=None,
        )
