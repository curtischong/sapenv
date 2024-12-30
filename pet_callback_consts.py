# pet callbacks
from typing import Any, Literal, Callable, Protocol

from pet import Pet

PetLevel = Literal[1, 2, 3]
Shop = Any  # prevent circular import
Team = Any
triggen_fn = Callable[[PetLevel, Shop, Team], None]


class OnSell(Protocol):
    def __call__(self, pet: Pet, shop: Shop, team: Team) -> None: ...


class OnBuy(Protocol):
    def __call__(self, pet: Pet, shop: Shop, team: Team) -> None: ...


class OnFaint(Protocol):
    def __call__(self, pet: Pet, team: Team) -> None: ...


class OnBattleStart(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]) -> None: ...


class OnLevelUp(Protocol):
    def __call__(self) -> None: ...
