from all_types_and_consts import Effect, Food, Species, Trigger
from battle import make_pet_faint
from pet import Pet
from shop import Shop
from team import Team


def trigger_food_globally(food_type: Food, team: Team, shop: Shop):
    match food_type:
        case Food.SALAD_BOWL:
            pets_to_buff = team.get_random_pets(2)
            attack_buff = 1
            health_buff = 1
        case Food.CANNED_FOOD:
            for slot in shop.slots:
                slot.pet.add_stats(attack=1, health=1)
            for slot in shop.linked_slots:
                slot.pet1.add_stats(attack=1, health=1)
                slot.pet2.add_stats(attack=1, health=1)
            shop.future_attack_addition += 1
            shop.future_health_addition += 1
            return
        case Food.SUSHI:
            pets_to_buff = team.get_random_pets(3)
            attack_buff = 1
            health_buff = 1
        case Food.PIZZA:
            pets_to_buff = team.get_random_pets(2)
            attack_buff = 2
            health_buff = 2
        case _:
            raise ValueError(f"Unknown food type: {food_type}")
    apply_food_buff(
        team=team,
        attack_buff=attack_buff,
        health_buff=health_buff,
        pets_to_buff=pets_to_buff,
    )


def trigger_food_for_pet(food_type: Food, team: Team, pet_idx: int, shop: Shop):
    pet = team.pets[pet_idx]
    attack_buff = 0
    health_buff = 0
    match food_type:
        case Food.APPLE:
            attack_buff = 1
            health_buff = 1
        case Food.HONEY:
            pet.effect = Effect.BEE
        case Food.PILL:
            make_pet_faint(
                pet, team_pets=team.pets, enemy_pets=None, is_in_battle=False
            )
        case Food.MEAT_BONE:
            pet.effect = Effect.MEAT_BONE
        case Food.CUPCAKE:
            num_times_to_apply_buff = get_num_times_to_apply_food_buff(team=team)
            pet.add_boost(
                attack=3 * num_times_to_apply_buff, health=3 * num_times_to_apply_buff
            )
        case Food.GARLIC:
            pet.effect = Effect.GARLIC
        case Food.PEAR:
            attack_buff = 2
            health_buff = 2
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
            attack_buff = 1
        case Food.MILK:
            attack_buff = 1
            health_buff = 2
        case Food.BETTER_MILK:  # stats for milk: https://superautopets.fandom.com/wiki/Cow
            attack_buff = 2
            health_buff = 4
        case Food.BEST_MILK:
            attack_buff = 3
            health_buff = 6
        case Food.APPLE_2_COST:
            attack_buff = 1
            health_buff = 1
        case Food.APPLE_2_COST_BETTER:
            attack_buff = 2
            health_buff = 2
        case Food.APPLE_2_COST_BEST:
            attack_buff = 3
            health_buff = 3
        case _:
            raise ValueError(f"Unknown food type: {food_type}")

    # does trigger_on_friendly_ate_food trigger if the pet ate a pill?
    apply_food_buff(
        team=team,
        attack_buff=attack_buff,
        health_buff=health_buff,
        pets_to_buff=[pet],
    )


def apply_food_buff(
    *,
    team: Team,
    attack_buff: int,
    health_buff: int,
    pets_to_buff: list[Pet],
):
    num_times_to_apply_buff = get_num_times_to_apply_food_buff(team=team)
    for pet in pets_to_buff:
        pet.add_stats(
            attack=attack_buff * num_times_to_apply_buff,
            health=health_buff * num_times_to_apply_buff,
        )
        trigger_on_friendly_ate_food(team=team, pet_that_ate_food=pet)


def get_num_times_to_apply_food_buff(team: Team):
    # use num_times_to_apply instead of a multiplier since cat buffs are additive NOT multiplicative: https://www.reddit.com/r/superautopets/comments/qsfhej/does_it_work_combo_megathread/
    num_times = 1
    for pet in team.pets:
        if pet.species == Species.CAT:
            num_buffs_in_turn = pet.metadata["num_times_buffed_food"]
            if num_buffs_in_turn >= 2:
                continue
            pet.metadata["num_times_buffed_food"] += 1

            num_times += pet.get_level()
    return num_times


def trigger_on_friendly_ate_food(team: Team, pet_that_ate_food: Pet):
    for friendly_pet in team.pets:
        friendly_pet.trigger(
            Trigger.ON_FRIENDLY_ATE_FOOD, pet_that_ate_food=pet_that_ate_food, team=team
        )
