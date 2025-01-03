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

TIGER_LEVEL_TRIGGER_KEY = "tiger_level_trigger"


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
                # important: determine if the tiger buff makes this trigger run twice BEFORE the trigger happens (since onfaint can mess up pet indexes)
                num_triggers, level_to_trigger_as = self.check_if_previous_pet_is_tiger(
                    trigger, **kwargs
                )
                if num_triggers == 0:
                    continue
                # the first arg is always the pet that's triggering the event. So we put "self" as the first arg
                self._triggers[trigger][ith_trigger](self, *args, **kwargs)

                if num_triggers == 2:
                    self.metadata[TIGER_LEVEL_TRIGGER_KEY] = level_to_trigger_as
                    self._triggers[trigger][ith_trigger](self, *args, **kwargs)
                ith_trigger += 1

    def check_if_previous_pet_is_tiger(self, trigger: Trigger, **kwargs):
        # ensure they are still in the team
        if "my_pets" in kwargs:
            my_pets: list[Pet] = kwargs["my_pets"]
        else:
            my_pets = kwargs["team"].pets

        # for some reason, pets can be gone from the team and this trigger is still called (note: we have an exception for fainted triggers. but still)
        # e.g. on battle start, even though we have an explicit if guard to ensure the pets are not in the team (before calling the trigger), it still calls
        # it's as if the list in the battle start is NOT updated. even though we only do mutations on the original ref object in this entire project
        # basically, this if statement is a final catch all to prevent triggers from hapepning if the pets are not in the team
        if "faint_pet_idx" not in kwargs and self not in my_pets:
            # print("my_pets listed", my_pets, self, trigger, kwargs)
            return 0, 0

        # 1) ensure that we are in a battle right now. the tiger only triggers in battle
        is_not_a_battle_trigger = trigger not in in_battle_triggers

        # I made sure that all triggers that can be in the shop or in battle will pass in a "is_in_battle" kwarg
        is_triggering_in_the_shop = (
            "is_in_battle" in kwargs and not kwargs["is_in_battle"]
        )
        if is_not_a_battle_trigger or is_triggering_in_the_shop:
            # the tiger can only trigger multiple times if it's in battle
            return 1, 0

        # 2) ensure that the pet behind this one is a tiger

        # get idx of the pet to check if the preivous pet is a tiger
        if "faint_pet_idx" in kwargs:
            # use this instead because for on_faint, we will NOT be able to find the index of the pet (after it's removed from the team)
            pet_idx = kwargs["faint_pet_idx"]
        else:
            pet_idx = my_pets.index(self)

        if (
            pet_idx > 0 and len(my_pets) > pet_idx - 1
        ):  # I'm really not sure why len(my_pets) > pet_idx - 1 can fail since we immediately call on_faint after we get the pet_idx
            # assert (
            #     len(my_pets) > pet_idx - 1
            # ), f"my_pets is not big enough my_pets={my_pets}" # my_pets is [] when this fails :/
            prev_index_pet = my_pets[pet_idx - 1]
            if prev_index_pet.species == Species.TIGER:
                return 2, prev_index_pet.get_level()
        return 1, 0

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
        if self.metadata[TIGER_LEVEL_TRIGGER_KEY] != 0:
            level_to_trigger_as = self.metadata[TIGER_LEVEL_TRIGGER_KEY]
            self.metadata[TIGER_LEVEL_TRIGGER_KEY] = 0
            return level_to_trigger_as

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
