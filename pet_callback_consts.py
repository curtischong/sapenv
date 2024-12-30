# pet callbacks
from enum import Enum, auto
from typing import Any, Literal, Callable, Protocol

from pet import Pet

PetLevel = Literal[1, 2, 3]
Shop = Any  # prevent circular import
Team = Any


class Trigger(Enum):
    ON_SELL = auto()
    ON_BUY = auto()
    ON_FAINT = auto()
    ON_DAMAGE = auto()
    ON_BATTLE_START = auto()
    ON_LEVEL_UP = auto()


TriggerFn = Callable[[Pet, Any], None]


class OnSell(Protocol):
    def __call__(self, pet: Pet, shop: Shop, team: Team) -> None: ...


class OnBuy(Protocol):
    def __call__(self, pet: Pet, team: Team) -> None: ...


class OnFaint(Protocol):
    def __call__(self, pet: Pet, team: Team) -> None: ...


class OnBattleStart(Protocol):
    def __call__(self, pet: Pet, my_pets: list[Pet], enemy_pets: list[Pet]) -> None: ...


class OnLevelUp(Protocol):
    def __call__(self) -> None: ...
