from typing import Callable
from all_types_and_consts import MAX_ATTACK, MAX_HEALTH, Species
from pet import Pet
from pet_data import get_base_pet
import struct
import zlib

from team import Team


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


def compress_team(team: Team) -> bytes:
    # IMPROTANT: we do NOT save the temperary buffs. we just add it to the health and attack.
    # DO NOT load these pets directly and put them into a shop. because the temporary buffs will appear to be permaneny buffs.
    """
    Convert a list of Pet objects into a compressed binary blob.

    Each Pet is assumed to have:
        - pet.species.value (int)   -> stored in 2 bytes
        - pet.attack (int)          -> stored in 2 bytes
        - pet.health (int)          -> stored in 2 bytes
        - pet.experience (int)      -> stored in 2 bytes

    You can adjust the struct format and compression to suit your ranges & needs.
    """
    # Preallocate a bytearray so appending is efficient
    buffer = bytearray()

    # Pack each Pet’s attributes using a fixed 2-byte representation (big-endian)
    for pet in team.pets:
        buffer += struct.pack(">H", pet.species.value)
        buffer += struct.pack(">H", min(pet.attack + pet.attack_boost, MAX_ATTACK))
        buffer += struct.pack(">H", min(pet.health + pet.health_boost, MAX_HEALTH))
        buffer += struct.pack(">H", pet.experience)

    # Now compress the blob (zlib level=9 is the highest compression)
    compressed_blob = zlib.compress(buffer, level=9)
    return compressed_blob


def decompress_team(blob: bytes) -> list[Pet]:
    decompressed = zlib.decompress(blob)
    pets: list[Pet] = []
    # Read 8 bytes for each pet (4 x 2-byte fields)
    chunk_size = 2 * 4
    for i in range(0, len(decompressed), chunk_size):
        species_val, attack, health, exp = struct.unpack(
            ">HHHH", decompressed[i : i + chunk_size]
        )
        # Turn these back into a Pet
        # NOTE: You may need to map species_val -> PetSpeciesEnum
        pet = get_base_pet(Species(species_val)).set_stats_all(
            attack=attack,
            health=health,
            experience=exp,
        )
        pets.append(pet)
    return Team(pets)
