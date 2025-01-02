# sapenv

I chose not to use ECS in this because there are so few entities it doesn't maek sense
the game is also pretty simple, so it shouldn't be too hard to maintain


effects are handled NOT by trigger functions since effects can be overridden. it's much easier to just change the pet's effect attribute than to go looking for triggers to change.
So effects are handled by custom if logic on specific events (e.g. on_hurt when the pet takes damage)


pets that have an "works x time per turn" effect:
- ox
- rabbit
- gorilla
- hippo (works 3 times per battle)


tests to run:
fainting offers permanent stats buffs
horse stats disapepar after battle. but will help them win the battle

To fix:
- squirrel
- implement tiger
parrot. ENSURE IT copies the ability FIRST (so when on_end_turn is called, it can repeat on_end_turn effects)


I think that before a pet’s trigger is ran, we just need to verify that it’s still alive on the team. so each trigger needs to pass in the team. not sure how this will work with on_faint

one thing we should probably do is run an agent against all pets in the db to determine a smarter reward.