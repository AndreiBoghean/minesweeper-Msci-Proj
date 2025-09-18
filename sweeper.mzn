%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% representing the board state START
% we have a map of every mine of the field. we dont actually need that.. all our model needs is the grid of neighbour counts.

int: fieldWidth;
set of int: fieldIndexes = 1..fieldWidth*fieldWidth;
array[fieldIndexes] of 0..1: field; % the field of mines, where a 1 indicates that square has a mine.

set of int: fieldIndexesOnlyBorders = 1..fieldWidth union % top row
                                      (fieldWidth*(fieldWidth-1))..(fieldWidth*fieldWidth) % bottom row
                                      union {x*fieldWidth+1-fieldWidth | x in 1..fieldWidth} % left column
                                      union {x*fieldWidth | x in 1..fieldWidth}; % right column
set of int: fieldIndexesNoBorders   = fieldIndexes diff fieldIndexesOnlyBorders;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% neighbourMines definition START
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

output [
    "field = \(field)\n",
    "neighbourMines = \(neighbourMines)\n",
    "test = \([ (i,j): i*3+j | i in 2..4, j in 1..3][2,2])\n",
]
