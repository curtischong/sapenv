import numpy as np
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
        species: Species,
        attack: int,
        health: int,
        experience: PetExperience,
        # effect: Effect | None,  # TODO: add effect
        effect=None,
        on_level_up=dummy_trigger_fn,
        on_buy=dummy_trigger_fn,
    ):
        self.species = species
        self.attack = attack
        self.health = health
        self.experience = experience
        self.effect = effect
        self.on_level_up = on_level_up
        self.on_buy = on_buy

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

    def get_level_experience(self):
        if self.experience == 6:
            return 0
        if self.experience >= 3:  # the pet is on level 2.
            return self.experience - 3
        return self.experience  # the pet is on level 1. no need to subtract anything

    def combine_onto(self, pet2: "Pet"):
        pet1 = self
        if pet2._has_higher_stats(pet1):
            # important. use pet2 first. So if both have equal stats, we'll USE pet2 (due to the implementation of has_higher_stats)
            stats_to_add = pet1.experience
            updated_pet = pet2.add_stats(attack=stats_to_add, health=stats_to_add)
        else:
            stats_to_add = pet2.experience
            updated_pet = pet1.add_stats(attack=stats_to_add, health=stats_to_add)

        # now update the experience
        old_level = updated_pet.get_level()
        updated_pet.experience = min(
            pet1.experience + pet2.experience, MAX_PET_EXPERIENCE
        )
        new_level = updated_pet.get_level()

        # call the on_level_up function if the pet leveled up
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

    def set_stats(self, *, attack: int, health: int):
        self.attack = attack
        self.health = health
        return self

    # TODO: add effect
    def set_stats_all(self, *, attack: int, health: int, experience: int):
        self.attack = attack
        self.health = health
        self.experience = experience
        return self

    @staticmethod
    def get_base_stats_observation(pets: list["Pet"]):
        num_pets = len(pets)
        species = np.zeros((len(Species), num_pets), dtype=bool)
        attacks = np.zeros((num_pets,), dtype=np.int32)
        healths = np.zeros((num_pets,), dtype=np.int32)

        for idx, pet in enumerate(pets):
            species[pet.species.value, idx] = 1
            attacks[idx] = pet.attack
            healths[idx] = pet.health

        return {
            "species": species,
            "attacks": attacks,
            "healths": healths,
        }

    def __repr__(self):
        level = self.get_level()
        level_experience = self.get_level_experience()
        # TODO: print effect
        return f"{self.species.name}: {self.attack}🗡 {self.health}\u2764\ufe0f lvl{level}-{level_experience}"

    def state(self):
        return {
            "species": self.species.value,
            "attack": self.attack,
            "health": self.health,
            "experience": self.experience,
        }
