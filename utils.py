from typing import Callable
from all_types_and_consts import Species
from pet_data import get_base_pet


# this function is a bit sus since it modifies the original array AND returns the modified array
def extend_array_to_length[T](
    arr: list[T], length: int, get_padded_value: Callable[[], T]
):
    if len(arr) > length:
        raise ValueError(
            f"arr must be less than or equal to length, actual value: {arr}"
        )
    while len(arr) < length:
        arr.append(get_padded_value())
    return arr


def extend_pet_array_to_length(arr: list[Species], length: int):
    return extend_array_to_length(
        arr, length, get_padded_value=lambda: get_base_pet(Species.NONE)
    )


def require_consent(prompt: str):
    response = input(prompt).strip().lower()
    if response != "yes":
        print("Operation canceled.")
        exit(0)
