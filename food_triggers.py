from all_types_and_consts import Effect, Food, Species, Trigger
from battle import make_pet_faint
from pet import Pet
from pet_data import get_base_pet
from shop import Shop
from team import Team


def trigger_food_globally(food_type: Food, team: Team, shop: Shop):
    match food_type:
        case Food.SALAD_BOWL:
            pets = team.get_random_pets(2)
            for pet in pets:
                pet.add_stats(attack=1, health=1)
                trigger_on_friendly_ate_food(team=team, pet_that_ate_food=pet)
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
                trigger_on_friendly_ate_food(team=team, pet_that_ate_food=pet)
        case Food.PIZZA:
            pets = team.get_random_pets(2)
            for pet in pets:
                pet.add_stats(attack=2, health=2)
                trigger_on_friendly_ate_food(team=team, pet_that_ate_food=pet)
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
        case Food.BETTER_MILK:  # stats for milk: https://superautopets.fandom.com/wiki/Cow
            pet.add_stats(attack=2, health=4)
        case Food.BEST_MILK:
            pet.add_stats(attack=3, health=6)
        case Food.APPLE_2_COST:
            pet.add_stats(attack=1, health=1)
        case Food.APPLE_2_COST_BETTER:
            pet.add_stats(attack=2, health=2)
        case Food.APPLE_2_COST_BEST:
            pet.add_stats(attack=3, health=3)
        case _:
            raise ValueError(f"Unknown food type: {food_type}")

    # does this trigger if the pet ate a pill?
    trigger_on_friendly_ate_food(team=team, pet_that_ate_food=pet)


def trigger_on_friendly_ate_food(team: Team, pet_that_ate_food: Pet):
    for friendly_pet in team.pets:
        friendly_pet.trigger(
            Trigger.ON_FRIENDLY_ATE_FOOD, pet_that_ate_food=pet_that_ate_food, team=team
        )
