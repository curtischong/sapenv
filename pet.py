from all_types_and_consts import (
    MAX_PET_EXPERIENCE,
    PetExperience,
    Species,
    dummy_trigger_fn,
)


class Pet:
    def __init__(
        self,
        *,
        species: str,
        attack: int,
        health: int,
        experience: PetExperience,
        # effect: Effect | None,  # TODO: add effect
        effect=None,
        on_level_up=dummy_trigger_fn,
    ):
        self.species = species
        self.attack = attack
        self.health = health
        self.experience = experience
        self.effect = effect
        self.on_level_up = on_level_up

    @staticmethod
    def define_base_stats(*, species: Species, attack: int, health: int):
        return Pet(
            species=species,
            attack=attack,
            health=health,
            experience=1,
            effect=None,
        )

    def clone(self):
        return Pet(
            species=self.species,
            attack=self.attack,
            health=self.health,
            experience=self.experience,
            effect=self.effect,
        )

    def __eq__(self, other: "Pet"):
        return (
            self.species == other.species
            and self.attack == other.attack
            and self.health == other.health
            and self.experience == other.experience
            and self.effect == other.effect
        )

    def get_level(self):
        if self.experience < 3:
            return 1
        elif self.experience < 6:
            return 2
        else:
            return 3

    def combine_onto(self, pet2: "Pet"):
        pet1 = self
        if pet2._has_higher_stats(pet1):
            # important. use pet2 first. So if both have equal stats, we'll USE pet2 (due to the implementation of has_higher_stats)
            updated_pet = pet2.add_stats(attack=1, health=1)
        else:
            updated_pet = pet1.add_stats(attack=1, health=1)

        old_level = updated_pet.get_level()
        # now update the experience
        updated_pet.experience = min(
            pet1.experience + pet2.experience, MAX_PET_EXPERIENCE
        )
        new_level = updated_pet.get_level()
        if new_level > old_level:
            updated_pet.on_level_up()

        return updated_pet

    def _has_higher_stats(self, other: "Pet"):
        self_stats = self.attack + self.health
        other_stats = other.attack + other.health
        return self_stats >= other_stats

    def add_stats(self, *, attack: int, health: int):
        self.attack += attack
        self.health += health
        return self
