import numpy as np
from scipy.signal import convolve2d

def printGrid(grid):
    for row in grid:
        for cell in row:
            if cell == 0: print(" ")
            if cell == 9: print("X")

testCase = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0]
]
testCase = np.array(testCase)
input = testCase


kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
hints = convolve2d(input, kernel, "same")

# for each "label" (mine, not mine) we maintain a list of whether it's in-bounds for a given cell. at first, every cell has all possible labels, i.e. both cell and mine.
# the first index, i.e. domains[:,:,0] coresponds to the empty label
# and the second index, i.e. domains[:,:,1] coresponds to the empty label
domains = np.ones((input.shape[0], input.shape[1], 2))

print(hints)
# print(domains)
# printGrid(testCase)
# printGrid(hints)

# with our domains set up, we now need constraints between domains according to the hints.

######### CONSTRAINT HELPERS.. these make little sense on their own.. look at the constraints section first.

# for each available spot:
#     pick the current spot.
#     if we need more picks, recursively call ourselves on the spots to the right

def spot_pick(arrangementTemplate, leftI, spotN): # assumes spotN is at least 1; leftI is within bounds.
    arrangements = []
    for chosenI in range(leftI, len(arrangementTemplate)):
        # print("outer", chosenI, leftI, len(arrangementTemplate))
        newTemplate = arrangementTemplate[:] # duplicate array
        newTemplate[chosenI] = True # mark as chosen

        if spotN-1 > 0:
            moreArrangements = spot_pick(newTemplate, chosenI+1, spotN-1)
            arrangements.extend(moreArrangements)
        else:
            arrangements.append(newTemplate)

    return arrangements

def parse_arrangement(arrangement):
    return "".join(["1" if val else "_" for val in arrangement])
############### CONSTRAINTS
# at a high-level, we follow the simple constraint:
# for every hint, the sum of mines in its neighbours is equal to the hint number.

# for use with GAC, RAC2, RAC3,
# we further break this down into the possible combinations of mines e.g.
# for a hint of 1, there is either 1 mine top-left and no mine elsewhere, or 1 mine top and no mine elsewhere, or 1 mine top-right and no mine elsewhere, etc.
# with increasing combinations for more mines.

print("arrangements test")

# testSpot = spot_pick([False]*8, 0, 7)
# for arr in testSpot:
#     print(parse_arrangement(arr))

for i in range(9):
    testSpot = spot_pick([False]*8, 0, i)
    print("hints:", i, "positions:", len(testSpot))

print("building constraints")

constraints = []
variableToConstraints = {}
constraintsToVariables = {}

for y in range(input.shape[0]):
    for x in range(input.shape[1]):
        hintCount = input[y][x]

        arrangements = []
        # now we need to make a unique constraint for every combination of mines among the neighbours.
        if hintCount > 0:
            arrangementTemplate = [False]*8 # start with a blank arrangement
            arrangements = spot_pick(arrangementTemplate, 0, hintCount)
        else:
            arrangements = [False]*8 # a hint of 0 means all neighbours are forced to be open

        # we now have our "arrangements"
        # we want to store the fact that arrangements[0] OR arrangements[1] OR arrangements[2] ... etc.
        # and put that in our constraints storage
        # in some form that lets us use it.

        # what is "some form that lets us use it"?
        # well how will we ever need to use it?
            # CP algorithms seem to like to iterate over constraints that operate on a variable.
            # and also variables used by a constraint.

        # alternatively..
        # general workflow: start with variable, get constraints upon it, and then get those variables in those constraints.
        # first step: variable to constraint
        # second step: constraint to variables

        # first attempt:
        constraintID = len(constraints) # get the "ID" of the new constraint

        constraints.append(arrangements)
        # this only needs to dictate the logic of the constraint.. i.e. what it does with its variables and how it gets validated.
        # since we're operating with only a single constraint (lucky!) we can simplify the constraint logic to just the set of valid arrangements
        # instead of arbitrary logic.

        relevantVariables = [] # temporary list with all the variables this constraint influences
        for y2 in range(y-1, y+2):
            for x2 in range(x-1, x+2):
                if not (y2 < 0 or y2 >= input.shape[0] or x2 < 0 or x2 >= input.shape[1]): # if the neighbour is within bounds
                    relevantVariables.append((x2, y2))

        constraintsToVariables[constraintID] = relevantVariables
        for var in relevantVariables: variableToConstraints[var] = variableToConstraints.get(var, []) + [constraintID] # WARN: creating a new array each time..

print(domains)
print("_____________________")
print(constraints)
print("_____________________")
print(variableToConstraints)
print("_____________________")
print(constraintsToVariables)
print("_____________________")
