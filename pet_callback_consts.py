# pet callbacks
from typing import Any, Literal, Callable, Protocol

from pet import Pet

PetLevel = Literal[1, 2, 3]
Shop = Any  # prevent circular import
Team = Any
triggen_fn = Callable[[PetLevel, Shop, Team], None]


class OnSell(Protocol):
    def __call__(self, pet_level: PetLevel, shop: Shop, team: Team) -> None: ...


class OnBuy(Protocol):
    def __call__(self, pet_level: PetLevel, shop: Shop, team: Team) -> None: ...


class OnFaint(Protocol):
    def __call__(self, pet_level: PetLevel, team: Team) -> None: ...


class OnBattleStart(Protocol):
    def __call__(
        self, pet_level: PetLevel, my_pets: list[Pet], enemy_pets: list[Pet]
    ) -> None: ...
