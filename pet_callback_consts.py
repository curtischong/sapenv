# pet callbacks
from typing import Any, Literal, Callable, Protocol

PetLevel = Literal[1, 2, 3]
Shop = Any  # prevent circular import
Team = Any
triggen_fn = Callable[[PetLevel, Shop, Team], None]


class OnSell(Protocol):
    def __call__(self, pet_level: PetLevel, shop: Shop, team: Team) -> None: ...
