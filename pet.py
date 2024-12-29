import numpy as np
from all_types_and_consts import (
    MAX_ATTACK,
    MAX_HEALTH,
    MAX_PET_EXPERIENCE,
    Effect,
    PetExperience,
    Species,
    dummy_trigger_fn,
)
from pet_callback_consts import OnBattleStart, OnBuy, OnFaint, OnSell


class Pet:
    def __init__(
        self,
        *,
        species: Species,
        attack: int,
        health: int,
        experience: PetExperience,
        # effect: Effect | None,  # TODO: add effect
        effect: Effect = Effect.NONE,
        attack_boost: int = 0,
        health_boost: int = 0,
        on_level_up=dummy_trigger_fn,
        on_buy: OnBuy = dummy_trigger_fn,
        on_sell: OnSell = dummy_trigger_fn,
        on_faint: OnFaint = dummy_trigger_fn,
        on_hurt: OnFaint = dummy_trigger_fn,
        on_battle_start: OnBattleStart = dummy_trigger_fn,
    ):
        self.species = species
        self.attack = attack
        self.health = health
        self.experience = experience
        self.effect = effect
        self.attack_boost = attack_boost
        self.health_boost = health_boost
        self.on_level_up = on_level_up
        self.on_buy = on_buy
        self.on_sell = on_sell
        self.on_faint = on_faint
        self.on_hurt = on_hurt
        self.on_battle_start = on_battle_start

    @staticmethod
    def define_base_stats(*, species: Species, attack: int, health: int):
        return Pet(
            species=species,
            attack=attack,
            health=health,
            experience=1,
            effect=None,
        )

    def set_on_sell(self, on_sell: OnSell):
        self.on_sell = on_sell

    def set_on_buy(self, on_sell: OnBuy):
        self.on_sell = on_sell

    def set_on_faint(self, on_faint: OnFaint):
        self.on_faint = on_faint

    def set_on_battle_start(self, on_battle_start: OnBattleStart):
        self.on_battle_start = on_battle_start

    def clone(self):
        return Pet(
            species=self.species,
            attack=self.attack,
            health=self.health,
            experience=self.experience,
            effect=self.effect,
            attack_boost=self.attack_boost,
            health_boost=self.health_boost,
            on_level_up=self.on_level_up,
            on_buy=self.on_buy,
            on_sell=self.on_sell,
            on_faint=self.on_faint,
            on_hurt=self.on_hurt,
            on_battle_start=self.on_battle_start,
        )

    def __eq__(self, other: "Pet"):
        return (
            self.species == other.species
            and self.attack == other.attack
            and self.health == other.health
            and self.experience == other.experience
            and self.effect == other.effect
            and self.attack_boost == other.attack_boost
            and self.health_boost == other.health_boost
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

    # shop is empty to prevent circular import
    def combine_onto(self, pet2: "Pet", shop):
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
            shop.create_linked_pet()

        return updated_pet

    def _has_higher_stats(self, other: "Pet"):
        self_stats = self.attack + self.health
        other_stats = other.attack + other.health
        return self_stats >= other_stats

    def add_stats(self, *, attack: int, health: int):
        self.attack = min(MAX_ATTACK, self.attack + attack)
        self.health = min(MAX_HEALTH, self.health + health)
        return self

    def set_stats(self, *, attack: int, health: int):
        self.attack = attack
        self.health = health
        return self

    def add_boost(self, *, attack: int, health: int):
        self.attack_boost += attack
        self.health_boost += health

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
