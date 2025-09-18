% I'm trying to think of this problem in terms of what the initial environment is, how the player can influence that, and the final environment the player is aiming for, using it's available actions on the initial state.

% &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& representing the board state.. (the environment)
% first thing's first: we have squares. each square has values 0:hidden 1:empty, NOT 2:flagged
% ^ note: I dont think we need the flagged state.. going to try without it
% also, we have a playing field, that is an NxN grid.
int: fieldWidth;
set of int: fieldIndexes = 1..fieldWidth*fieldWidth;
array[fieldIndexes] of 0..1: field; % the field of mines, where a 1 indicates that square has a mine.
set of int: fieldIndexesOnlyBorders = 1..fieldWidth union % top row
                                      (fieldWidth*(fieldWidth-1))..(fieldWidth*fieldWidth) % bottom row
                                      union {x*fieldWidth+1-fieldWidth | x in 1..fieldWidth} % left column
                                      union {x*fieldWidth | x in 1..fieldWidth}; % right column
set of int: fieldIndexesNoBorders   = fieldIndexes diff fieldIndexesOnlyBorders;

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

% naive probability attempt
% pre-requsite.. a list of neighbouring mines for each cell.
% ^ note: this is basically just convolution with kernel [[1, 1, 1], [1, 0, 1], [1, 1, 1]] (i.e. sum our neighbours; exclude middle)
array[fieldIndexes] of var 0..8: neighbourMines;
constraint forall (fieldIndex in fieldIndexesNoBorders) (
    neighbourMines[fieldIndex] = field[fieldIndex-1-fieldWidth] + field[fieldIndex-fieldWidth] + field[fieldIndex+1-fieldWidth]
                               + field[fieldIndex-1           ]                 +                field[fieldIndex+1           ]
                               + field[fieldIndex-1+fieldWidth] + field[fieldIndex+fieldWidth] + field[fieldIndex+1+fieldWidth]
);

% border columns, excluding corners
/*
notes:
- we +/- fieldWidth to go down/up.
- we shift the edgePoint according to the hOffset (i.e. are we left edge or right edge)
- if we're on right edge, then we subtract 1 MORE from the right side of the summing kernel, to bring it behind the middle,
  because we need to flip it, because the "centre" is the one that is on the edge of the board.
*/
% constraint forall (hOffset in 0..1, edgePoint in {x | x in 1+(1+hOffset*(fieldWidth-1))*fieldWidth..(fieldWidth-1+hOffset*(fieldWidth-1))*fieldWidth where x mod fieldWidth = 1-hOffset}) (
% the edgePoint set takes advantage of the fact that the right-most cell's index is always a factor of the field width.
% similarly, the left-most cell in each row will be equal to 1 plus a multiple of fieldWidth.
constraint forall (hOffset in 0..1, edgePoint in {x | x in fieldWidth+1..fieldWidth*(fieldWidth-1) where x mod fieldWidth = 1-hOffset}) (
    neighbourMines[edgePoint] = field[edgePoint-fieldWidth] + field[edgePoint-fieldWidth-2*hOffset+1]
                                                            + field[edgePoint           -2*hOffset+1]
                              + field[edgePoint+fieldWidth] + field[edgePoint+fieldWidth-2*hOffset+1]
);
% similarly for border rows
% notice I've removed the *fieldWidth from the edgePoint range, because we're no longer stepping vertically through rows, but moving left to right, IN a row.
% relI is offset to the bottom of the board, turning it into the bottom row, only if vOffset=1.
constraint forall (vOffset in 0..1, edgePoint in {relI+(fieldWidth*(fieldWidth-1))*vOffset | relI in (2)..(fieldWidth-1)}) (
    neighbourMines[edgePoint] = field[edgePoint-1                          ]                 +                              field[edgePoint+1                          ]
                              + field[edgePoint-1+fieldWidth*(-2*vOffset+1)] + field[edgePoint+fieldWidth*(-2*vOffset+1)] + field[edgePoint+1+fieldWidth*(-2*vOffset+1)]
);

% final edge cases for corners.. laid out in a table cuz I was feeling neat and tidy
%                                                        field[position                   right left down          up           ]
constraint neighbourMines[1]                           = field[1                           +1*1 -0*1 +0*fieldWidth -0*fieldWidth] +
                                                         field[1                           +0*1 -0*1 +1*fieldWidth -0*fieldWidth] +
                                                         field[1                           +1*1 -0*1 +1*fieldWidth -0*fieldWidth];
constraint neighbourMines[fieldWidth]                  = field[fieldWidth                  +0*1 -1*1 +0*fieldWidth -0*fieldWidth] +
                                                         field[fieldWidth                  +0*1 -0*1 +1*fieldWidth -0*fieldWidth] +
                                                         field[fieldWidth                  +0*1 -1*1 +1*fieldWidth -0*fieldWidth];
constraint neighbourMines[1+fieldWidth*(fieldWidth-1)] = field[1+fieldWidth*(fieldWidth-1) +1*1 -0*1 +0*fieldWidth -0*fieldWidth] +
                                                         field[1+fieldWidth*(fieldWidth-1) +0*1 -0*1 +0*fieldWidth -1*fieldWidth] +
                                                         field[1+fieldWidth*(fieldWidth-1) +1*1 -0*1 +0*fieldWidth -1*fieldWidth];
constraint neighbourMines[fieldWidth*fieldWidth]       = field[fieldWidth*fieldWidth       +0*1 -1*1 +0*fieldWidth -0*fieldWidth] +
                                                         field[fieldWidth*fieldWidth       +0*1 -0*1 +0*fieldWidth -1*fieldWidth] +
                                                         field[fieldWidth*fieldWidth       +0*1 -1*1 +0*fieldWidth -1*fieldWidth];

% now we use neighbourMines to build the naive mine probability table.
% problem: the known probabilities change according to how much of the board we've discovered.
% do we
%   A: keep a probability table for each turn (needlessly memory intensive?)
%   B: find a smarter way

% what could a smarter way look like? well, we know the player's action sequence.
% we could restrict player actions so they can only open a square, if the required actions to guarantee a square's safety were taken
%   ^ i.e. I can only open this square if I've opened the square above it, and the square to the left.
%   which is the information I would hypothetically need to be able to open the square without worry.

% how could we figure out what moves are required to deem a square "safe"?.
% idk... :(

% after thought and deliberation.. we shouldnt be thinking in terms of probability a cell has a mine,
% but rather probabilities of shapes.
% if an open cell has 2 neighbouring mine, and 3 neighbouring possible positions, there are 3 potential "shapes" that are likely: "XX0, 0XX, X0X".
% we need to think in terms of these shapes, and then selectively eliminate shapes according to info suggested by other cells.

% we do this with binary.
% luckily 8 bit numbers exist, and a 3x3 grid without the middle is coincidentally 8 items.
% each bit dictates yes or no for a mine being present in the coresponding square.

%     sidenote: 2^8=256 numbers in a list for a single cell, with each number being 8 bits or 1 byte.
%     so with a 50x50 grid we will have 640000 numbers for the whole grid. a.k.a. 640 kilobytes. this may have performance ramifications :(

% ok time to do some real work.
% array[fieldIndexes, 8] of var 0..1: localShapes;
% ^ not too sure how to name this properly. it's an array the size of the minefield, where each entry is a flag dictating whether the corresponding neighbour is a mine.


output [
    "field = \(field)\n",
    "visitedCells = \(array2set(absolutePositions))\n",
    "neighbourMines = \(neighbourMines)\n",
    "\n",
    "absolutePositions = \(absolutePositions)\n",
    "moveDecisions = \(moveDecisions)\n",
    "revealDecisions = \(revealDecisions)\n",
    "didOpen = \(didOpen)\n",
    % "test = \(1..fieldWidth)\n",
    % "test = \((fieldWidth*(fieldWidth-1))..(fieldWidth*fieldWidth))\n",
    % "test = \({x*fieldWidth+1-fieldWidth | x in 1..fieldWidth})\n",
    % "test = \({x*fieldWidth | x in 1..fieldWidth})\n",
]





% &&&&&&&&&&&&&&&&&& sanity check: what is the "gameplay" element?
% &&&&&&&&& talking through our logic..
% so, we have a 1d array or maybe a matrix telling us whether each cell is a mine or not.
% what does the theoretical ideal solution look like in this game?
% would that be the turtle starting in the top left and scanning along, simply skipping?
% well, yes, if the turtle knew.
% what we're trying to simulate is ambiguity.
% even if we managed to get some degree of ambiguity, what do we use it for?
% the intended flow is that the turtle circles the block and finds the "entry".
% how can we coax this behaviour in the iterative execution that is CP?

% &&&&&&&&& what we should do..
% SOLUTION: we must forbid gambles. the turtle must only take moves that are certain.
% we must still allow gambles in the minefield, but must somehow forbid impossible problems.
% these gambling conditions AVOID THIS BEING A SIMPLE PATHFINDING PROBLEM

% &&&&&&&&& how can we implement probability considerations.. (the hard part; lots of words here.)
% okok we've figured out how to work around AMBIGUITY.
% but HOW DO WE SELECTIVELY REVEAL?

% at any given time, the agent's knowledge of the playing field consists of it's own history.
% can we forbit it from being wrong by simply requiring it never open a mine or flag a safe cell?
% if we did that, would it encroach on our "ambiguity exists" constraints?

% &&&&& (naive) probability with sum of neighbours
% to know this, we need to think more about how we allow ambiguity. each cell's mine percentage is given by the minimum of a simple algorithm run over all neighbouring open cells.
% if an open cell's value is e.g. 3, then the unrevealed cell's bomb probability is given by that open cell's value, divided by the amount of unopen cells in the vicinity.
% so if that open cell has 4 neighbouring cells that are unrevealed, we know there's a 3/4 or 75% chance one of those unrevealed cells contain a mine.

% keeping this in mind.. to forbid gambling, we must maintain a matrix with a cell's given mine probability at any turn. we then constrain the "reveal" action to only work on 0% probability cells.
% further, to forbid mine arrangements that require a gamble, we can state that the player eventually finishes the game. with the "player never takes gambles" rules, THIS SHOULD ULTIMATELY IMPLY THE PLAYING FIELD NEVER FORCES A GAMBLE.

% &&&&& realising the naive attempt is naive
% implementing probability..
% we COULD have an array of t fields for all turns, tracking how the probability changes on each turn
% but that would be wasteful? I think.
% getting ahead of myself.. how do we do this?
% if we calculate a cell's probability solely on it's neighbours, we miss out on 80% of the fun of minesweeper, where you're kinda using baye's theorem with multiple different cells
% to find out that a particular cell has a 0% mine probability, despite the fact that it's immediate neighbours dont necessarily suggest that.

% take for example this minesweeper arrangement. we're studying the left border where the 1 and 2 neighbour each other.
% the "A" are minesweeper cells purely aflicted by the SINGLE 1 at the border.
% the "B" are cells influenced by both the 1 and the 2, because those cells are in range of both.
% the "C" are cells purely influenced by the 2 in the border. (NOT ALL 2s. just the one at the border)
% ..._ABBC___...
% ...11122111...
% there is a single mine in the 3 cells "ABB". the neighbouring 2 indicates there is 2 mines in the 3 cells "BBC"
% there is an overlap of 2 cells between the domain of the 1 and the domain of the 2. (the overlapping cells being "BB")
% a human realises that the `1` suggests it is impossible for both mines from the `2` to be in "BB", hence one mine MUST be in position C.
% a human would subsequently understand there is 1 mine left in the range of the `2`, i.e. there's 1 cell in "BB"
% therefore slot A is empty.

% this sort of deductive reasoning is what we want to maximise in this minizinc model
% but to maximise it, the model must be able to do it. how do we make it possible?

% ...3344422...
% ...1112111...

% ok new new idea..
% when considering an open cell, we look at it's number and all it's neighbours.
% we go through all possible permutations of mines within the cells,
% and for each cell it's "value" becomes the count of combinations where the cell has a mine
% a problem arises when there's only 1 combination, with everything being a mine
% because then everything is 1, but we want high mine certainty to be a high mine value
% we should divide by the total number of combinations
% ^ this actually doeesnt work at all I think (because all the permutations even out..) but whatever

% .. what if sum of ALL neighbours MINUS (1 + (DIRECT neighbours) MOD 2). (intent is that even number subtracts 1)
% ^^ trying to work through this with some diagrams I wont understand tomorrow.. VV
% ...3343433...
% ...1112111...

% ...3355533...
% ...1113111...

% ...3355533...
% ...__131__...
% ...__1X1__...

% &&&&& comming to terms with my foolishness and returning to the naive method.
/*
ABSOLUTE RULE: because we need to specially consider cases when e.g. a [1] guarantees a cell has a mine, I think we will require a MAX somewhere in our weightings.
this is kinda the naive method. I feel like a more complex attempt may require the naive version in the first place. this is why..
cope: we try to start with a naive immeidate neighbour probability approach, and see what happens then go from there. I've spent too much time trying to think this over
*/


% &&&&&&&&&&&&&&&&&& back to the rules of simple minesweeper
% this was a useful tangent, but we now return to the core of minesweeper.
% how can we ensure our turtle doesnt break the rules?
% I suspect "only open 0% mine cells" should cover everything we need, really,
% so it remains to be seen when we give a proper go at the implementation
