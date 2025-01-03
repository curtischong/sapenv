# sapenv

This is a modern Super Auto Pets RL environment for the Turtle Pack. Here's why I wrote my own env:
- It shows linked pets (in the shop) when a pet is leveled up.
- You can make better design decisions if you are making the environment AND training the RL agent afterwards (e.g. other suepr auto pets have an action that allows the model to pick from one of 5! possible reorders. In this environment, reordering pets is done by simply selecting 2 indexes - making the action space more compact. This also makes sense from a human perspective because when you reorder pets, you are directly considering which index a single pet would be better in, NOT how all the pets should be rearranged)
- The action space and action space mask are defined next to each other, making it much simpler to read the code and detect bugs.
- I didn't like how other envs used json to specify pet triggers. This env offers compile-time guarantees (or on start of runtime guarantees) for trigger definitions with functions
- The action and state space uses gymnasium Dicts. I then use custom flattening logic to wrangle it for the model. However, when you are developing, it's so much simpler and easier to see all of the state/action space when it's presented in a dict. No need for thinking about bit manipulation!
- Other environments used openAI gym (which is now unsupported). This env uses gymnasium

#### Design considerations
I chose not to use ECS in this because there are so few entities it doesn't maek sense
the game is also pretty simple, so it shouldn't be too hard to maintain


Effects are NOT handled by trigger functions since effects can be overridden. it's much easier to just change the pet's effect attribute than to go looking for triggers to change.
So effects are handled by custom if logic on specific events (e.g. on_hurt when the pet takes damage)



#### Improvements
- one thing we should probably do is run an agent against all pets in the db to determine a smarter reward. Right now, we only sample one opposing team from the DB to get the reward. however, a larger samping pool would make hte reward signla less fuzzy and ofer convergence quicker


#### Tests to add
- parrot. ENSURE IT copies the ability FIRST (so when on_end_turn is called, it can repeat on_end_turn effects)
- fainting offers permanent stats buffs
- horse stats disapepar after battle. but will help them win the battle
