# sapenv

I chose not to use ECS in this because there are so few entities it doesn't maek sense
the game is also pretty simple, so it shouldn't be too hard to maintain


effects are handled NOT by callback functions since effects can be overridden. it's much easier to just change the pet's effect attribute than to go looking for callbacks to change.
So effects are handled by custom if logic on specific events (e.g. on_hurt when the pet takes damage)
