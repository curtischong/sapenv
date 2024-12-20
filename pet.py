from all_types_and_consts import PetExperience, PetLevel, Species


class Pet:
    def __init__(
        self,
        *,
        species: str,
        attack: int,
        health: int,
        level: PetLevel,
        experience: PetExperience,
        # effect: Effect | None,  # TODO: add effect
        effect=None,
    ):
        self.species = species
        self.attack = attack
        self.health = health
        self.level = level
        self.experience = experience
        self.effect = effect

    @staticmethod
    def define_base_stats(*, species: Species, attack: int, health: int):
        return Pet(
            species=species,
            attack=attack,
            health=health,
            level=1,
            experience=1,
            effect=None,
        )

    def clone(self):
        return Pet(
            species=self.species,
            attack=self.attack,
            health=self.health,
            level=self.level,
            experience=self.experience,
            effect=self.effect,
        )

    def __eq__(self, other: "Pet"):
        return (
            self.species == other.species
            and self.attack == other.attack
            and self.health == other.health
            and self.level == other.level
            and self.experience == other.experience
            and self.effect == other.effect
        )

    def has_higher_stats(self, other: "Pet"):
        self_stats = self.attack + self.health
        other_stats = other.attack + other.health
        return self_stats >= other_stats

    def update_stats(self, delta_attack: int, delta_health: int):
        self.attack += delta_attack
        self.health += delta_health
        return self
