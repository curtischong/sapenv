from all_types_and_consts import Effect, Food, Species, Trigger
from battle import make_pet_faint
from pet_data import get_base_pet
from shop import Shop
from team import Team


def trigger_food_globally(food_type: Food, team: Team, shop: Shop):
    match food_type:
        case Food.SALAD_BOWL:
            pets = team.get_random_pets(2)
            for pet in pets:
                pet.add_stats(attack=1, health=1)
        case Food.CANNED_FOOD:
            for slot in shop.slots:
                slot.pet.add_stats(attack=1, health=1)
            for slot in shop.linked_slots:
                slot.pet1.add_stats(attack=1, health=1)
                slot.pet2.add_stats(attack=1, health=1)
            shop.future_attack_addition += 1
            shop.future_health_addition += 1
        case Food.SUSHI:
            pets = team.get_random_pets(3)
            for pet in pets:
                pet.add_stats(attack=1, health=1)
        case Food.PIZZA:
            pets = team.get_random_pets(2)
            for pet in pets:
                pet.add_stats(attack=2, health=2)
        case _:
            raise ValueError(f"Unknown food type: {food_type}")


def trigger_food_for_pet(food_type: Food, team: Team, pet_idx: int, shop: Shop):
    pet = team.pets[pet_idx]
    match food_type:
        case Food.APPLE:
            pet.add_stats(attack=1, health=1)
        case Food.HONEY:
            pet.effect = Effect.BEE
        case Food.PILL:
            make_pet_faint(
                pet, team_pets=team.pets, enemy_pets=None, is_in_battle=False
            )
        case Food.MEAT_BONE:
            pet.effect = Effect.MEAT_BONE
        case Food.CUPCAKE:
            pet.add_boost(attack=3, health=3)
        case Food.GARLIC:
            pet.effect = Effect.GARLIC
        case Food.PEAR:
            pet.add_stats(attack=2, health=2)
        case Food.CHILI:
            pet.effect = Effect.CHILLI
        case Food.CHOCOLATE:
            old_level = pet.get_level()
            pet.experience += 1
            new_level = pet.get_level()
            if new_level > old_level:
                pet.trigger(Trigger.ON_LEVEL_UP)
                shop.create_linked_pet()
        case Food.STEAK:
            pet.effect = Effect.STEAK
        case Food.MELON:
            pet.effect = Effect.MELON
        case Food.MUSHROOM:
            pet.effect = Effect.MUSHROOM

        # hidden foods
        case Food.BREAD_CRUMB:
            pet.add_stats(attack=1)
        case Food.MILK:
            pet.add_stats(attack=1, health=2)
        case Food.APPLE_2_COST:
            pet.add_stats(attack=1, health=1)
        case Food.APPLE_2_COST_BETTER:
            pet.add_stats(attack=2, health=2)
        case Food.APPLE_2_COST_BEST:
            pet.add_stats(attack=3, health=3)
        case _:
            raise ValueError(f"Unknown food type: {food_type}")
