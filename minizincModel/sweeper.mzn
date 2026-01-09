%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% representing the board state START
% we have a map of every mine of the field. we dont actually need that.. all our model needs is the grid of neighbour counts.

int: fieldWidth;
array[1..fieldWidth, 1..fieldWidth] of 0..1: field; % the field of mines, where a 0 indicates a covered cell, and a 1 indicates an opened cell.
array[1..fieldWidth, 1..fieldWidth] of -1..8: neighbourMines; % a -1 indicates a cell is un-opened.
array[1..fieldWidth, 1..fieldWidth] of var 0..1: newField; % 0 for covered, 1 for opened.

% if a cell was previously opened, then it is still opened.
constraint forall (fieldX in 1..fieldWidth, fieldY in 1..fieldWidth) (
    if field[fieldX, fieldY] == 1 then newField[fieldX, fieldY] == 1 endif
);

% /*
% for a given open cell, it's non-opened neighbours is at least the number of mines in the cell.
% for all neighbours that arent opened cells, their sums equal the amount of mines in the vicinity.
constraint forall (fieldX in 1..fieldWidth, fieldY in 1..fieldWidth) (
    if (neighbourMines[fieldY, fieldX] != -1) then
        neighbourMines[fieldY, fieldX] <= 8 -
            (if fieldY-1 < 1 then 3 else
                 if fieldX-1 >= 1          then newField[fieldY-1, fieldX-1] else 1 endif +
                                                newField[fieldY-1, fieldX  ]              +
                 if fieldX+1 <= fieldWidth then newField[fieldY-1, fieldX+1] else 1 endif
            endif
        +
            if fieldX-1 >= 1          then newField[fieldY, fieldX-1] else 1 endif +
            if fieldX+1 <= fieldWidth then newField[fieldY, fieldX+1] else 1 endif
        +
            if fieldY+1 > fieldWidth then 3 else
                 if fieldX-1 >= 1           then newField[fieldY+1, fieldX-1] else 1 endif +
                                                 newField[fieldY+1, fieldX  ]              +
                 if fieldX+1 <= fieldWidth  then newField[fieldY+1, fieldX+1] else 1 endif
            endif)
    endif
);

% if it's impossible to deduce info for a cell (it has no open neighbours), then we dont deduce anything.
constraint forall (fieldX in 1..fieldWidth, fieldY in 1..fieldWidth) (
    if -8 ==
        (if fieldY-1 < 1 then -3 else
            if fieldX-1 >= 1          then neighbourMines[fieldY-1, fieldX-1] else -1 endif +
                                           neighbourMines[fieldY-1, fieldX  ]               +
            if fieldX+1 <= fieldWidth then neighbourMines[fieldY-1, fieldX+1] else -1 endif
        endif
        +
        if fieldX-1 >= 1          then neighbourMines[fieldY, fieldX-1] else -1 endif +
        if fieldX+1 <= fieldWidth then neighbourMines[fieldY, fieldX+1] else -1 endif
        +
        if fieldY+1 > fieldWidth then -3 else
            if fieldX-1 >= 1           then neighbourMines[fieldY+1, fieldX-1] else -1 endif +
                                            neighbourMines[fieldY+1, fieldX  ]               +
            if fieldX+1 <= fieldWidth  then neighbourMines[fieldY+1, fieldX+1] else -1 endif
        endif)
    then newField[fieldX, fieldY] == 0 endif

);

% */

solve maximize sum(newField);
% solve satisfy;

output "field:\n";
output [row: "\(field[row, 1..fieldWidth])\n" | row in 1..fieldWidth];
output "\n";

output "neighbourMines:\n";
output [row: "\(neighbourMines[row, 1..fieldWidth])\n" | row in 1..fieldWidth];
output "\n";

output "newField:\n";
output [row: "\(newField[row, 1..fieldWidth])\n" | row in 1..fieldWidth];
