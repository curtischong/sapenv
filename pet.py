from typing import Callable
import numpy as np
from all_types_and_consts import (
    MAX_ATTACK,
    MAX_HEALTH,
    MAX_PET_EXPERIENCE,
    BattleResult,
    Effect,
    PetExperience,
    Species,
    Trigger,
)
from typing import Any, Protocol

Shop = Any  # prevent circular import
Team = Any


class OnSell(Protocol):
    def __call__(self, pet: "Pet", shop: Shop, team: Team) -> None: ...


class OnBuy(Protocol):
    def __call__(self, pet: "Pet", team: Team) -> None: ...


class OnFaint(Protocol):
    def __call__(
        self, pet: "Pet", team_pets: list["Pet"], is_in_battle: bool
    ) -> None: ...


class OnHurt(Protocol):
    def __call__(self, pet: "Pet", team_pets: list["Pet"]) -> None: ...


class OnBattleStart(Protocol):
    def __call__(
        self, pet: "Pet", my_pets: list["Pet"], enemy_pets: list["Pet"]
    ) -> None: ...


class OnLevelUp(Protocol):
    def __call__(self) -> None: ...


class OnSummonedFriend(Protocol):
    def __call__(
        self, pet: "Pet", summoned_friend: "Pet", is_in_battle: bool
    ) -> None: ...


class OnEndTurn(Protocol):
    def __call__(
        self, pet: "Pet", team: "Team", last_battle_result: BattleResult
    ) -> None: ...


# TODO: ensure triggers follow these interfaces
TriggerFn = Callable[
    [
        OnSell
        | OnBuy
        | OnFaint
        | OnHurt
        | OnBattleStart
        | OnLevelUp
        | OnSummonedFriend
        | OnEndTurn
    ],
    None,
]


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
    ):
        self.species = species
        self.attack = attack
        self.health = health
        self.experience = experience
        self.effect = effect
        self.attack_boost = attack_boost
        self.health_boost = health_boost

        self._triggers: dict[Trigger, TriggerFn] = {}
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
        self._triggers[trigger] = trigger_fn

    # call triggers that the pet has
    def trigger(self, trigger: Trigger, *args, **kwargs) -> None:
        if trigger in self._triggers:
            if trigger == Trigger.ON_FRIEND_SUMMONED:
                assert self is not kwargs["summoned_friend"]
            # the first arg is always the pet that's triggering the event
            self._triggers[trigger](self, *args, **kwargs)

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
        for trigger, trigger_fn in self._triggers.items():
            pet.set_trigger(trigger, trigger_fn)

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

    def get_level(self) -> int:
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
            updated_pet.trigger(Trigger.ON_LEVEL_UP)
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

    def apply_temp_buffs(self):
        self.add_stats(attack=self.attack_boost, health=self.health_boost)
        return self

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
