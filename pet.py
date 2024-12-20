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

    def get_total_experience(self):
        exp = self.experience
        if self.level == 2:
            exp += 3
        if self.level == 3:
            exp += 6
        return exp

    def combine_onto(self, pet2: "Pet"):
        pet1 = self
        if pet2._has_higher_stats(pet1):
            # important. use pet2 first. So if both have equal stats, we'll USE pet2 (due to the implementation of has_higher_stats)
            updated_pet = pet2.add_stats(attack=1, health=1)
        else:
            updated_pet = pet1.add_stats(attack=1, health=1)

        # how update the level and experience
        total_experience = pet1.level * pet1.experience + pet2.experience

        return updated_pet

    def _has_higher_stats(self, other: "Pet"):
        self_stats = self.attack + self.health
        other_stats = other.attack + other.health
        return self_stats >= other_stats

    def add_stats(self, *, attack: int, health: int):
        self.attack += attack
        self.health += health
        return self
