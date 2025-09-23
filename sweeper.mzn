%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% representing the board state START
% we have a map of every mine of the field. we dont actually need that.. all our model needs is the grid of neighbour counts.

int: fieldWidth;
array[1..fieldWidth, 1..fieldWidth] of 0..1: field; % the field of mines, where a 1 indicates that square has a mine.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% neighbourMines definition START
% pre-requsite.. a list of neighbouring mines for each cell.
% ^ note: this is basically just convolution with kernel [[1, 1, 1], [1, 0, 1], [1, 1, 1]] (i.e. sum our neighbours; exclude middle)
array[1..fieldWidth, 1..fieldWidth] of var 0..8: neighbourMines;
constraint forall (fieldX in 1..fieldWidth, fieldY in 1..fieldWidth) (
    neighbourMines[fieldY, fieldX] =
        if fieldY-1 < 1 then 0 else
             if fieldX-1 < 1 then 0 else field[fieldY-1, fieldX-1] endif +
             field[fieldY-1, fieldX  ] +
             if fieldX+1 > fieldWidth then 0 else field[fieldY-1, fieldX+1] endif
        endif
    +
         if fieldX-1 < 1 then 0 else field[fieldY  , fieldX-1] endif +
         if fieldX+1 > fieldWidth then 0 else field[fieldY  , fieldX+1] endif
    +
        if fieldY+1 > fieldWidth then 0 else
             if fieldX-1 < 1 then 0 else field[fieldY+1, fieldX-1] endif +
             field[fieldY+1, fieldX  ] +
             if fieldX+1 > fieldWidth then 0 else field[fieldY+1, fieldX+1] endif
        endif
);
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

array[1..fieldWidth, 1..fieldWidth] of var 0..1: cellDecisions; % 0 for open, 1 for mine.

array[1..fieldWidth, 1..fieldWidth] of var allTurns: timings;
% /*
% an action can happen only after an action on it's neighbour happens first.
constraint forall (fieldX in 1..fieldWidth, fieldY in 1..fieldWidth) (
        if fieldY-1 >= 1 then
             if fieldX-1 >= 1 then          timings[fieldY-1, fieldX-1] > timings[fieldY, fieldX] endif \/
                                            timings[fieldY-1, fieldX  ] > timings[fieldY, fieldX] \/
             if fieldX+1 <= fieldWidth then timings[fieldY-1, fieldX+1] > timings[fieldY, fieldX] endif
        endif \/

        if fieldX-1 >= 1 then          timings[fieldY, fieldX-1] > timings[fieldY, fieldX] endif \/
        if fieldX+1 <= fieldWidth then timings[fieldY, fieldX+1] > timings[fieldY, fieldX] endif \/

        if fieldY+1 <= fieldWidth then
             if fieldX-1 >= 1 then          timings[fieldY+1, fieldX-1] > timings[fieldY, fieldX] endif \/
                                            timings[fieldY+1, fieldX  ] > timings[fieldY, fieldX] \/
             if fieldX+1 <= fieldWidth then timings[fieldY+1, fieldX+1] > timings[fieldY, fieldX] endif
        endif
);
% */

% /*
% for all neighbours that arent opened cells, their sums equal the amount of mines in the vicinity.
constraint forall (fieldX in 1..fieldWidth, fieldY in 1..fieldWidth) (
    neighbourMines[fieldY, fieldX] =
        if fieldY-1 < 1 then 0 else
             if fieldX-1 >= 1          /\ (timings[fieldY-1, fieldX-1] > timings[fieldY, fieldX] \/ cellDecisions[fieldY-1, fieldX-1] == 1) then cellDecisions[fieldY-1, fieldX-1] else 0 endif +
             if                           (timings[fieldY-1, fieldX  ] > timings[fieldY, fieldX] \/ cellDecisions[fieldY-1, fieldX  ] == 1) then cellDecisions[fieldY-1, fieldX  ] else 0 endif +
             if fieldX+1 <= fieldWidth /\ (timings[fieldY-1, fieldX+1] > timings[fieldY, fieldX] \/ cellDecisions[fieldY-1, fieldX+1] == 1) then cellDecisions[fieldY-1, fieldX+1] else 0 endif
        endif
    +
         if fieldX-1 >= 1          /\ (timings[fieldY, fieldX-1] > timings[fieldY, fieldX] \/ cellDecisions[fieldY, fieldX-1] == 1) then cellDecisions[fieldY, fieldX-1] else 0 endif +
         if fieldX+1 <= fieldWidth /\ (timings[fieldY, fieldX+1] > timings[fieldY, fieldX] \/ cellDecisions[fieldY, fieldX+1] == 1) then cellDecisions[fieldY, fieldX+1] else 0 endif
    +
        if fieldY+1 > fieldWidth then 0 else
             if fieldX-1 >= 1          /\ (timings[fieldY+1, fieldX-1] > timings[fieldY, fieldX] \/ cellDecisions[fieldY+1, fieldX-1] == 1) then cellDecisions[fieldY+1, fieldX-1] else 0 endif +
             if                           (timings[fieldY+1, fieldX  ] > timings[fieldY, fieldX] \/ cellDecisions[fieldY+1, fieldX  ] == 1) then cellDecisions[fieldY+1, fieldX  ] else 0 endif +
             if fieldX+1 <= fieldWidth /\ (timings[fieldY+1, fieldX+1] > timings[fieldY, fieldX] \/ cellDecisions[fieldY+1, fieldX+1] == 1) then cellDecisions[fieldY+1, fieldX+1] else 0 endif
        endif
);
% */

constraint timings[1, 1] = 1; % temp fix: we start top-left corner.
% constraint timings[2, 1] = 6; % temp fix: we start top-left corner.
% constraint timings[2, 2] = 6; % temp fix: we start top-left corner.
% constraint timings[2, 3] = 6; % temp fix: we start top-left corner.
constraint count(timings, 1) = 1;
% constraint cellDecisions == field;
% solve satisfy;
solve minimize sum(timings);

output "field:\n";
output [row: "\(field[row, 1..fieldWidth])\n" | row in 1..fieldWidth];
output "\n";

output "neighbourMines:\n";
output [row: "\(neighbourMines[row, 1..fieldWidth])\n" | row in 1..fieldWidth];
output "\n";

output "timings:\n";
output [row: "\(timings[row, 1..fieldWidth])\n" | row in 1..fieldWidth];

output "cellDecisions:\n";
output [row: "\(cellDecisions[row, 1..fieldWidth])\n" | row in 1..fieldWidth];
output "\n";
