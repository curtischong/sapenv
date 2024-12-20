from pet import Pet
from shop import Shop
from pet_data import tier_1_pets, tier_2_pets, tier_3_pets


def test_shop_only_generates_pets_of_the_correct_tier():
    shop = Shop()
    shop.shop_tier = 3

    def get_species_in_tier(pets_in_tier: list[Pet]):
        return [pet.species for pet in pets_in_tier]

    pets_within_shop_tier = tier_1_pets + tier_2_pets + tier_3_pets
    species_within_shop_tier = set(get_species_in_tier(pets_within_shop_tier))

    num_rolls = 30
    for _ in range(num_rolls):
        shop.roll_shop()
        for slot in shop.slots:
            assert slot.pet.species in species_within_shop_tier
