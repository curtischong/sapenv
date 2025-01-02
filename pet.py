from collections import defaultdict
import numpy as np
from all_types_and_consts import (
    MAX_ATTACK,
    MAX_HEALTH,
    MAX_PET_EXPERIENCE,
    Effect,
    PetExperience,
    PetLevel,
    Species,
    Trigger,
    in_battle_triggers,
)
from typing import Any


TriggerFn = Any  # prevent circular import
Shop = Any  # prevent circular import
Team = Any  # prevent circular import


class Pet:
    def __init__(
        self,
        *,
        species: Species,
        attack: int,
        health: int,
        experience: PetExperience,
        effect: Effect = Effect.NONE,
        attack_boost: int = 0,
        health_boost: int = 0,
    ):
        self.species = species
        self.attack = attack
        self.health = health
        self.experience = experience
        self.effect = effect
        self.attack_boost = attack_boost
        self.health_boost = health_boost

        # e.g. extra info for each pet. e.g. for a rabbit: the number of times a friendly ate food this turn
        # the way to use metadata is this: whenever the cooldown refreshes, we clear the metadata (so all counts are reset to 0)
        # This means: to implement a cooldown, just add 1 to the metadata counter and check if it's greater than the cooldown amount
        self.metadata = defaultdict(int)

        self._triggers: dict[Trigger, list[TriggerFn]] = defaultdict(list)
        # self.id = uuid.uuid4() # I don't think this is needed since each python object has a unique id. And we use .index() to get the right index of a pet in a list (or "is" to check for equality)

    @staticmethod
    def define_base_stats(*, species: Species, attack: int, health: int):
        return Pet(
            species=species,
            attack=attack,
            health=health,
            experience=1,
        )

    def set_trigger(self, trigger: Trigger, trigger_fn: TriggerFn):
        self._triggers[trigger].append(trigger_fn)

    # call triggers that the pet has
    def trigger(self, trigger: Trigger, *args, **kwargs) -> None:
        if trigger == Trigger.ON_FRIEND_SUMMONED:
            assert self is not kwargs["summoned_friend"]

        # only run the trigger if the pet has it
        if trigger in self._triggers:
            # a trigger may append MORE triggers of the same type. So we cannot just use a "for in" loop.
            ith_trigger = 0
            while ith_trigger < len(self._triggers[trigger]):
                # the first arg is always the pet that's triggering the event. So we put "self" as the first arg
                self._triggers[trigger][ith_trigger](self, *args, **kwargs)
                self.try_trigger_twice_tiger(trigger, ith_trigger, *args, **kwargs)
                ith_trigger += 1

    def try_trigger_twice_tiger(
        self, trigger: Trigger, ith_trigger: int, *args, **kwargs
    ):
        is_not_a_battle_trigger = trigger not in in_battle_triggers

        # I made sure that all triggers that can be in the shop or in battle will pass in a "is_in_battle" kwarg
        is_triggering_in_the_shop = (
            "is_in_battle" in kwargs and not kwargs["is_in_battle"]
        )
        if is_not_a_battle_trigger or is_triggering_in_the_shop:
            # the tiger can only trigger multiple times if it's in battle
            return

        if "my_pets" in kwargs:
            my_pets: list[Pet] = kwargs["my_pets"]
        else:
            my_pets = kwargs["team"].pets

        # get idx of the pet to check if the preivous pet is a tiger
        if "faint_pet_idx" in kwargs:
            # use this instead because for on_faint, we will NOT be able to find the index of the pet (after it's removed from the team)
            pet_idx = kwargs["faint_pet_idx"]
        else:
            if (
                self in my_pets
            ):  # e.g. if in an on_battle_start trigger is queued, but the whale dies before it runs, we won't find the whale on the team. so skip it
                pet_idx = my_pets.index(self)
            else:
                pet_idx = -1

        prev_index_pet_species = Species.NONE
        if (
            pet_idx > 0 and pet_idx - 1 < len(my_pets)
        ):  # pet_idx - 1 < len(my_pets) is super sus. I only added it because after a make_pet_faint fall, the pet behind it probably also died? so my_pets[pet_idx - 1] threw an exception
            # I think it's find to have this if statement just to avoid the exception. it feels like an edge case
            prev_index_pet_species = my_pets[pet_idx - 1].species
        if prev_index_pet_species == Species.TIGER:
            # the tigger behind this pet makes this trigger run twice
            print("trigger ran twice")
            self._triggers[trigger][ith_trigger](self, *args, **kwargs)

    def clear_triggers(self):
        self._triggers.clear()

    def copy_triggers(self, other: "Pet"):
        for trigger, trigger_fns in other._triggers.items():
            for trigger_fn in trigger_fns:
                self.set_trigger(trigger, trigger_fn)

    def clone(self):
        pet = Pet(
            species=self.species,
            attack=self.attack,
            health=self.health,
            experience=self.experience,
            effect=self.effect,
            attack_boost=self.attack_boost,
            health_boost=self.health_boost,
        )
        pet.copy_triggers(self)

        return pet

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

    def set_effect(self, effect: Effect):
        self.effect = effect
        return self

    def get_level(self) -> PetLevel:
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

    def combine_onto(self, pet2: "Pet", team: Team, shop: Shop):
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
            updated_pet.trigger(Trigger.ON_LEVEL_UP, team=team)
            shop.create_linked_pet()

        return updated_pet

    def _has_higher_stats(self, other: "Pet"):
        self_stats = self.attack + self.health
        other_stats = other.attack + other.health
        return self_stats >= other_stats

    def add_stats(self, *, attack: int = 0, health: int = 0):
        self.attack = min(MAX_ATTACK, self.attack + attack)
        self.health = min(MAX_HEALTH, self.health + health)
        return self

    def set_stats(self, *, attack: int, health: int):
        self.attack = attack
        self.health = health
        return self

    def add_boost(self, *, attack: int = 0, health: int = 0):
        self.attack_boost += attack
        self.health_boost += health

    def apply_temp_buffs(self):
        self.add_stats(attack=self.attack_boost, health=self.health_boost)
        return self

    def set_stats_all(
        self,
        *,
        attack: int,
        health: int,
        effect: Effect,
        experience: int,
        attack_boost: int,
        health_boost: int,
    ):
        self.attack = attack
        self.health = health
        self.effect = effect
        self.experience = experience
        self.attack_boost = attack_boost
        self.health_boost = health_boost
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
