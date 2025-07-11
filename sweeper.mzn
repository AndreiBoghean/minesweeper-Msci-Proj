first thing's first: we have a playing field.

on each turn, the agent specifies a move.

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& what the player IS
the player is effectively a turtle.
the player is "drawing" with either "flag" or "open" pixels, on a canvas.
the problem is a case of minimising how quickly the player draws the "correct" (winning) canvas.

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& what the player DOES
how do we "execute" the player's actions, so we can determine the amount of rounds they took?
well, the number of rounds is easily discernable from the length of the array for the player's actions
the complexity lies in checking that the player's actions actually produce a solution.

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& how the player WINS
therefore, I ask myself how do I check constraint satisfaction for a sequence of actions?
first, we realise that at any given point in the action sequence,
the turtle's position is a cummulative sum of their past movement actions.
however we must filter for movement actions only.
furthermore, minizinc has no concept of vectors so we will have to work in terms of index within a 1d array
- i.e. to move foward/backward we +/- 1, and to move up/down we +/1 the length of a row. (hence over/under flowing into the next/last row)

ok now we know how to check the player's actions are correct.
time for the player.

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& how the player PLAYS
so, we have a 1d array or maybe a matrix telling us whether each cell is a mine or not.
.. ok wait this whole idea might be stupid.
what does the theoretical ideal solution look like in this game?
would that be the turtle starting in the top left and scanning along, simply skipping?
well, yes, if the turtle knew.
what we're trying to simulate is ambiguity.
how can I ... sidenote: just realised, this might actually just be pathfinding basically lmao. since we're effectively letting the turtle know where the bombs are and asking it to find the most efficient path.
anyways.. is there a way to maintain ambiguity in this? we're not training an AI, so we cant be learning anything
wait..

okokokokok, even if we managed to get some degree of ambiguity, what do we use it for?
the intended flow is that the turtle circles the block and finds the "entry".
how can we coax this behaviour in the iterative execution that is CP?

SOLUTION: we must forbid gambles. the turtle must only take moves that are certain.
we must still allow gambles in the minefield, but must somehow forbid impossible problems.
these gambling conditions AVOID THIS BEING A SIMPLE PATHFINDING PROBLEM

okok we've figured out how to work around AMBIGUITY.
but HOW DO WE SELECTIVELY REVEAL?

at any given time, the agent's knowledge of the playing field consists of it's own history.
can we forbit it from being wrong by simply requiring it never open a mine or flag a safe cell?
if we did that, would it encroach on our "ambiguity exists" constraints?

to know this, we need to think more about how we allow ambiguity. each cell's mine percentage is given by the minimum of a simple algorithm run over all neighbouring open cells.
if an open cell's value is e.g. 3, then the unrevealed cell's bomb probability is given by that open cell's value, divided by the amount of unopen cells in the vicinity.
so if that open cell has 4 neighbouring cells that are unrevealed, we know there's a 3/4 or 75% chance one of those unrevealed cells contain a mine.

keeping this in mind.. to forbid gambling, we must maintain a matrix with a cell's given mine probability at any turn. we then constrain the "reveal" action to only work on 0% probability cells.
further, to forbid mine arrangements that require a gamble, we can state that the player eventually finishes the game. with the "player never takes gambles" rules, THIS SHOULD ULTIMATELY IMPLY THE PLAYING FIELD NEVER FORCES A GAMBLE.
