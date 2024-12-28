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
        case Food.SUSHI:
            team.add_milk()
        case Food.PIZZA:
            team.add_milk()
        case _:
            raise ValueError(f"Unknown food type: {food_type}")
