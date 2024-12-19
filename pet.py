from all_types import PetExperience, PetLevel


class Pet:
    def __init__(
        self,
        *,
        species: str,
        health: int,
        defence: int,
        level: PetLevel,
        experience: PetExperience,
        effect: Effect | None,
    ):
        self.species = species
        self.health = health
        self.defence = defence
        self.level = level
        self.experience = experience
        self.effect = effect

    @staticmethod
    def define_base_stats(species: str, health: int, defence: int):
        return Pet(
            species=species,
            health=health,
            defence=defence,
            level=1,
            experience=1,
            effect=None,
        )
