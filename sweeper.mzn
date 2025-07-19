% I'm trying to think of this problem in terms of what the initial environment is, how the player can influence that, and the final environment the player is aiming for, using it's available actions on the initial state.

% &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& representing the board state.. (the environment)
% first thing's first: we have squares. each square has values 0:hidden 1:empty, NOT 2:flagged
% ^ note: I dont think we need the flagged state.. going to try without it
% also, we have a playing field, that is an NxN grid.
int: fieldWidth;
int: fieldWidthSquared;
set of int: fieldIndexes = 1..fieldWidthSquared;
array[fieldIndexes] of 0..1: field; % the field of mines, where a 1 indicates that square has a mine.


% &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& representing player actions.. (how we interract with the environment)

% firstly, we remember from AE2 that minizinc doesnt let us have dynamic lists, so we must fix our array size.
int: maxTurns;
set of int: allTurns = 1..maxTurns;
set of int: allTurnsMinus1 = 1..maxTurns-1;

% the agent's possible actions could be 0:reveal 1:reveal+move 2: move.
% small problem actually.. the "move" actions have a direction, so we cant represent all actions with 3 values.
% we dont want the direction of movement to influence the "objective function" of course, and foresight tells me that we'll be wanting 2 distinct lists for moves and reveals anyways,
% so might as well separate movements and reveals into separate lists now instead of later.

% with this new approach we shall have 2 lists:
% one with effectively booleans dictating whether the player revealed the current square on this turn or not,
% and one with the direction of movement for this current turn. (either up,down,left,right, or none)


set of int: moveDirections = {0, -fieldWidth, 1, fieldWidth, -1}; % directions are dontMove, north, east, south, west
array[allTurns] of var moveDirections: moveDecisions;

set of int: revealOptions = 0..1;
array[allTurns] of var revealOptions: revealDecisions;


% ^ point of consideration: the original idea was a restricted FOV for the player, but in fact there's no need.
% the player is allowed to remember all of their past actions, and there is no other way by which squares can reveal, so
% a restricted FOV simply doesnt make sense.
% an argument could be made to allow the player to reveal squares within a limited range, but that should be an easy change after everything else is done.

% &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& representing the player's motivation.. (our player's GOAL environment state.. built using the aforementioned actions.. starting from the aforementioned beggining environment state)

% the player's motivation can be further broken down into
% what the player is ( this part doesnt directly correlate to any constraints, it's just a useful frame of reference to think in terms of )
% how to objectively evaluate an action sequence
% how to validate an action sequence actually wins the game
% how the player plays ( in this section I'm basically rambling.. rewrite pending. it basically just explores the idea of "gambling" in minesweeper, and explains how our inclusion of risks will make this model do interesting things.)

% &&&&&&&&&&&&&&&&&& what the player IS
% the player is effectively a turtle.
% the player is "drawing" with either "flag" or "open" pixels, on a canvas.
% the problem is a case of minimising how quickly the player draws the "correct" (winning) canvas.

% &&&&&&&&&&&&&&&&&& objectively evaluating a sequence of player actions (how good is this particular set of actions?)
% this is actually the easy part. just check how many rounds the player took.
% the complexity lies in checking that the player's actions actually produce a solution...

% &&&&&&&&&&&&&&&&&& validating a sequence of player actions (do the actions win the game of minesweeper)
% therefore, I ask myself how do I check constraint satisfaction for a sequence of actions?
% first, we realise that at any given point in the action sequence.. the turtle's position is a cummulative sum of their past movement actions.
% however we must filter for movement actions only.
% furthermore, minizinc has no concept of vectors so we will have to work in terms of index within a 1d array
% - i.e. to move foward/backward we +/- 1, and to move up/down we +/1 the length of a row. (hence over/under flowing into the next/last row)

constraint absolutePositions[1] = 1; % we start at the start (top-left corner).
% we have an array of the absolute position at each turn, obtained via "our next position will be our current position, plus the direction we moved in on that turn"
array[allTurns] of var fieldIndexes: absolutePositions;
constraint forall (turn in allTurnsMinus1) (
    absolutePositions[turn+1] = absolutePositions[turn] + moveDecisions[turn]
    % ^ at case turn=0, the player's position is always the top left, regardless of their movement.
    % the move decision applies only after the first ever position. that's why moveDecisions may seem offset

);

% now knowing where we are absolutely, we then obtain for each cell whether it was ever opened or remained closed.
array[fieldIndexes] of var 0..1: didOpen;
constraint forall (turn in allTurns) (
    didOpen[absolutePositions[turn]] = revealDecisions[turn]
);

% through testing.. if the turtle didnt explore part of the board, then it doesnt get constrained lol
% therefore we must encode that a cell is fixed to unopened if it's not been visited.
constraint forall (fieldIndex in fieldIndexes) (
    if not (fieldIndex in array2set(absolutePositions)) then didOpen[fieldIndex] = 0 endif
);
% ^ fun note I will be deleting soon: if you mistakenly put ..then fieldIndex = 0.. then you imply that
% "any fieldIndex not visited is 0".. i.e. the only field index you're allowed to not visit is index 0.

constraint field = didOpen;
solve maximize count(moveDecisions, 0);

output [
    "field = \(field)\n",
    "moveDecisions = \(moveDecisions)\n",
    "absolutePositions = \(absolutePositions)\n",
    "revealDecisions = \(revealDecisions)\n",
    "didOpen = \(didOpen)\n",
]

% &&&&&&&&&&&&&&&&&& sanity check: what is the "gameplay" element?
% so, we have a 1d array or maybe a matrix telling us whether each cell is a mine or not.
% what does the theoretical ideal solution look like in this game?
% would that be the turtle starting in the top left and scanning along, simply skipping?
% well, yes, if the turtle knew.
% what we're trying to simulate is ambiguity.
% even if we managed to get some degree of ambiguity, what do we use it for?
% the intended flow is that the turtle circles the block and finds the "entry".
% how can we coax this behaviour in the iterative execution that is CP?

% SOLUTION: we must forbid gambles. the turtle must only take moves that are certain.
% we must still allow gambles in the minefield, but must somehow forbid impossible problems.
% these gambling conditions AVOID THIS BEING A SIMPLE PATHFINDING PROBLEM

% okok we've figured out how to work around AMBIGUITY.
% but HOW DO WE SELECTIVELY REVEAL?

% at any given time, the agent's knowledge of the playing field consists of it's own history.
% can we forbit it from being wrong by simply requiring it never open a mine or flag a safe cell?
% if we did that, would it encroach on our "ambiguity exists" constraints?

% to know this, we need to think more about how we allow ambiguity. each cell's mine percentage is given by the minimum of a simple algorithm run over all neighbouring open cells.
% if an open cell's value is e.g. 3, then the unrevealed cell's bomb probability is given by that open cell's value, divided by the amount of unopen cells in the vicinity.
% so if that open cell has 4 neighbouring cells that are unrevealed, we know there's a 3/4 or 75% chance one of those unrevealed cells contain a mine.

% keeping this in mind.. to forbid gambling, we must maintain a matrix with a cell's given mine probability at any turn. we then constrain the "reveal" action to only work on 0% probability cells.
% further, to forbid mine arrangements that require a gamble, we can state that the player eventually finishes the game. with the "player never takes gambles" rules, THIS SHOULD ULTIMATELY IMPLY THE PLAYING FIELD NEVER FORCES A GAMBLE.


% &&&&&&&&&&&&&&&&&& back to the rules of simple minesweeper
% this was a useful tangent, but we now return to the core of minesweeper.
% how can we ensure our turtle doesnt break the rules?
% I suspect "only open 0% mine cells" should cover everything we need, really,
% so it remains to be seen when we give a proper go at the implementation
