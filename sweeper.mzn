%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% representing the board state START
% we have a map of every mine of the field. we dont actually need that.. all our model needs is the grid of neighbour counts.

int: fieldWidth;
array[1..fieldWidth, 1..fieldWidth] of 0..1: field; % the field of mines, where a 1 indicates that square has a mine.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% neighbourMines definition START
% pre-requsite.. a list of neighbouring mines for each cell.
% ^ note: this is basically just convolution with kernel [[1, 1, 1], [1, 0, 1], [1, 1, 1]] (i.e. sum our neighbours; exclude middle)
array[1..fieldWidth, 1..fieldWidth] of var 0..8: neighbourMines;
constraint forall (fieldIndexX in 2..fieldWidth-1, fieldIndexY in 2..fieldWidth-1) (
    neighbourMines[fieldIndexY, fieldIndexX] = field[fieldIndexY-1, fieldIndexX-1] + field[fieldIndexY-1, fieldIndexX  ] + field[fieldIndexY-1, fieldIndexX+1]
                                             + field[fieldIndexY  , fieldIndexX-1]                      +                  field[fieldIndexY  , fieldIndexX+1]
                                             + field[fieldIndexY+1, fieldIndexX-1] + field[fieldIndexY+1, fieldIndexX  ] + field[fieldIndexY+1, fieldIndexX+1]
);

% border columns, excluding corners
/*
notes:
- we shift the edgePoint according to the hOffset (i.e. are we left edge or right edge)
- if we're on right edge, then we subtract 1 MORE from the right side of the summing kernel, to bring it behind the middle,
  because we need to flip it, because the "centre" is the one that is on the edge of the board.
*/
constraint forall (xOffset in 0..1, y in 2..fieldWidth-1) (
    neighbourMines[y, 1+xOffset*(fieldWidth-1)] = field[y-1, 1+xOffset*(fieldWidth-1)] + field[y-1, 2+xOffset*(fieldWidth-3)]
                                                                                       + field[y  , 2+xOffset*(fieldWidth-3)]
                                                + field[y+1, 1+xOffset*(fieldWidth-1)] + field[y+1, 2+xOffset*(fieldWidth-3)]
);
% similarly for border rows
constraint forall (yOffset in 0..1, x in 2..fieldWidth-1) (
    neighbourMines[1+yOffset*(fieldWidth-1), x] = field[1+yOffset*(fieldWidth-1), x-1]             +                          field[1+yOffset*(fieldWidth-1), x+1]
                                                + field[2+yOffset*(fieldWidth-3), x-1] + field[2+yOffset*(fieldWidth-3), x] + field[2+yOffset*(fieldWidth-3), x+1]
);

% final edge cases for corners.. laid out in a table cuz I was feeling neat and tidy
%                                                        field[y_position down/up    x_position right/left]
constraint neighbourMines[1,1]                         = field[1          +1,        1          +1]+
                                                         field[1          +0,        1          +1]+
                                                         field[1          +1,        1          +0];
constraint neighbourMines[1, fieldWidth]               = field[1          +1,        fieldWidth -1]+
                                                         field[1          +0,        fieldWidth -1]+
                                                         field[1          +1,        fieldWidth -0];
constraint neighbourMines[fieldWidth, 1]               = field[fieldWidth -1,        1          +1]+
                                                         field[fieldWidth -0,        1          +1]+
                                                         field[fieldWidth -1,        1          +0];
constraint neighbourMines[fieldWidth, fieldWidth]      = field[fieldWidth -1,        fieldWidth -1]+
                                                         field[fieldWidth -0,        fieldWidth -1]+
                                                         field[fieldWidth -1,        fieldWidth -0];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% neighbourMines definition DONE

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% representing the board state DONE


% &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& representing player actions START
/*
now that we know neighbour mines, we need to create the illusion of board discovery for the model.
suppose we start with a single open square in the middle of the board
we would want the model to only see the middle.
we allow it to see more, only once it marks a square for opening.
upon opening, the model is allowed to see the value.

in a given turn, what square values the model is allowed to see is contingient on whether the model opened that value in a previous turn.
remember how our model "thinks"? (it determines flags and opens based on considering permutations of mines within a given 3x3 grid).
we apply reduced visibility of the board by applying the "thinking" constraints only on cells whintletch have been revealed.
effectively, this should mean the model only reasons about it cells it's been allowed to see.
^ concern: 

we will need a "time of opening" for cells.
this is to enable us to state "a cell will be open only if it has an open neighbour"
as a consequence, any and every cell in the time_of_opening grid will be strictly greater than the youngest neighbouring opening.
*/


% IN SUMMARY:
% the board can only flag/open cells with an open neighbour.
% ...AND.. for an opened cell, it's closed neighbours DEFINETLY contain x mines.

% firstly, we remember from AE2 that minizinc doesnt let us have dynamic lists, so we must fix our array size.
% note: likely, this only needs to be board size squared, since it's not possible for 0 progress each turn. we always have at least 1 square of progress.
int: maxTurns;
set of int: allTurns = 1..maxTurns;
set of int: allTurnsMinus1 = 1..maxTurns-1;

solve satisfy;

output "field:\n";
output [row: "\(field[row, 1..fieldWidth])\n" | row in 1..fieldWidth];
output "\n";

output "neighbourMines:\n";
output [row: "\(neighbourMines[row, 1..fieldWidth])\n" | row in 1..fieldWidth];
