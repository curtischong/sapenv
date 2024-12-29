from all_types_and_consts import Food
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
            pass
        case Food.PILL:
            pet.on_
        case Food.MEAT_BONE:
            pass
        case Food.CUPCAKE:
            pass
        case Food.GARLIC:
            pass
        case Food.PEAR:
            pet.add_stats(attack=2, health=2)
        case Food.CHILI:
            pass
        case Food.CHOCOLATE:
            old_level = pet.get_level()
            pet.experience += 1
            new_level = pet.get_level()
            if new_level > old_level:
                pet.on_level_up()
                shop.create_linked_pet()
        case Food.STEAK:
            pass
        case Food.MELON:
            pass
        case Food.MUSHROOM:
            pass

        case _:
            raise ValueError(f"Unknown food type: {food_type}")
