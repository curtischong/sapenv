from all_types_and_consts import Species
from pet import Pet
from pet_data import get_base_pet


def extend_pet_array_to_length(arr: list[Pet], length: int):
    if arr > length:
        raise ValueError(
            f"arr must be less than or equal to length, actual value: {arr}"
        )
    while len(arr) < length:
        arr.append(get_base_pet(Species.NONE))
