from all_types_and_consts import Species
from pet_data import get_base_pet
from team import Team


def get_pig_team(round_number: int):
    additional_stats = round_number - 1
    return Team(
        [
            get_base_pet(Species.PIG).add_stats(
                attack=additional_stats, health=additional_stats
            ),
            get_base_pet(Species.PIG).add_stats(
                attack=additional_stats, health=additional_stats
            ),
            get_base_pet(Species.PIG).add_stats(
                attack=additional_stats, health=additional_stats
            ),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
        ]
    )


def get_horse_team(round_number: int):
    additional_stats = round_number - 1
    return Team(
        [
            get_base_pet(Species.HORSE).add_stats(attack=0, health=additional_stats),
            # get_base_pet(Species.HORSE),
            get_base_pet(Species.HORSE),
            get_base_pet(Species.HORSE),
            get_base_pet(Species.NONE),
            get_base_pet(Species.NONE),
        ]
    )
