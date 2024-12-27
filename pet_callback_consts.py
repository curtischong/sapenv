# pet callbacks
from typing import Literal, Callable, Protocol

from shop import Shop
from team import Team


PetLevel = Literal[1, 2, 3]
triggen_fn = Callable[[PetLevel, Shop], None]


class OnSell(Protocol):
    def __call__(self, pet_level: PetLevel, shop: Shop, team: Team) -> None: ...
