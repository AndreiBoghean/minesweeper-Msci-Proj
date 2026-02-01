import numpy as np
from scipy.signal import convolve2d
import copy
# import curses

# stdscr = curses.initscr()

########## RANDOM MINESWEEPER-SPECIFIC STUFF
def renderGrid(grid):
    for row in grid:
        for cell in row:
            if cell == 9: print("X") # mine hints dont go to 9, so we hijact to use 9 as the ID for a mine.
            else: print (" ")

########################################## FULL CONTROL INPUT CREATION

testCaseMines1 = np.array([
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0]
])
# random note relevant to "todo" variable..
# 12 from corners
# 5*(4+4+1+1)=5*10=50 from edges
# 8*4=32 from full cells
# 12+50+32=94 total todo items

testCaseMines2 = np.array([
    [0, 0],
    [1, 1],
])

testCaseMines3 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
])


testCase4 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 9, 1, 0, 0, 0],
    [0, 0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
])

testCase5 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 9, 1, 0, 0, 0],
    [0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
])

testCase6 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 9, 1, 0, 0, 0],
    [0, 0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
])

# FUTURE NOTE: test case 5 is solved correctly.. test case 6 isnt.
chosenTestCase = testCase6

testCaseMines = np.copy(chosenTestCase)
testCaseMines[chosenTestCase != 1] = 0

testCaseHidden = np.copy(chosenTestCase)
testCaseHidden[testCaseHidden != 9] = 0


# choose mine arrangement.. # grid of 0s and 1s for safe, not safe
mines = testCaseMines

# create hints.. 0-8
kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
hints = convolve2d(mines, kernel, "same")

# choose hiddens arrangement.. grid of 0s and 1s for revealed, hidden
hiddens = testCaseHidden

# build final input.. 0-8 for hint, 9 for hidden. # HACK: using 9 to represent covered cells in the hints representation.
input = hints # start from the hints
input[mines==1] = 9 # remove the hints that are actually mines
input[hiddens!=0] = 9 # remove the hints that are not visible.


################# PARTIAL CONTROL INPUT PARSING
testCasePAPERv1 = np.array([
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 0],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2, 1, 1, 1, 0],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 0],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1, 0, 1, 1],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2, 1, 2, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 2, 1, 2, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 1, 1, 1, 1, 0, 2, 9, 4, 2, 1],
    [9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
    [9, 9, 2, 2, 3, 2, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [9, 9, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 9, 1, 0],
    [9, 9, 3, 3, 3, 2, 1, 1, 9, 1, 0, 0, 1, 1, 1, 0],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 0, 0, 0]
])

testCasePAPERv2 = np.array([
    [0, 0, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1],
    [0, 0, 1, 1, 2, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [0, 0, 2, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [0, 0, 2, 9, 9, 9, 9, 9, 9, 9, 2, 1, 3, 9, 9, 9],
    [0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 2, 0, 1, 9, 9, 9],
    [1, 1, 1, 9, 9, 9, 9, 9, 9, 9, 2, 0, 1, 1, 2, 1],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2, 0, 0, 0, 0, 0],
    [9, 2, 2, 1, 2, 3, 9, 2, 2, 1, 1, 1, 1, 1, 0, 0],
    [9, 9, 2, 0, 0, 1, 9, 1, 0, 0, 0, 1, 9, 1, 0, 0],
    [9, 9, 3, 1, 1, 1, 9, 1, 0, 0, 0, 2, 9, 2, 0, 0],
    [9, 9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 1, 9, 2, 1, 0],
    [9, 9, 9, 9, 9, 9, 9, 2, 1, 0, 0, 1, 2, 9, 2, 1],
    [9, 9, 9, 9, 9, 9, 9, 9, 2, 1, 0, 0, 2, 9, 9, 9],
    [9, 9, 9, 9, 9, 3, 1, 2, 9, 1, 0, 1, 3, 9, 3, 1],
    [9, 9, 9, 9, 9, 3, 0, 1, 1, 1, 0, 1, 9, 9, 2, 0],
    [9, 9, 9, 9, 9, 2, 0, 0, 0, 0, 0, 1, 9, 9, 1, 0]
])

hints = testCasePAPERv1

print("hints:")
print(hints)
print()




####### DOMAINS

def renderDomains(domains):

    

    colGRAY = '\033[90m'
    hcolGRAY = '\033[100m'
    hbcolGRAY = '\033[100;5m'
    colPURPLE = '\033[95m'
    hcolPURPLE = '\033[105m'
    colRED = '\033[91m'
    hcolRED = '\033[101m'
    hbcolRED = '\033[101;5m'
    colRESTORE = '\033[0m'

    colBLUE = '\033[34m'
    hcolBLUE = '\033[44m'
    hbcolBLUE = '\033[44;5m'
    colGREEN = '\033[32m'
    hcolGREEN = '\033[42m'
    hbcolGREEN = '\033[42;5m'
    colYELLOW = '\033[33m'
    hcolYELLOW = '\033[43m'
    hbcolYELLOW = '\033[43;5m'

    for y, row in enumerate(hints):
        for x, cell in enumerate(row):
            if domains[(x, y)] == [True, True]:
                print(hcolGRAY + "?", end=colRESTORE)
            elif domains[(x, y)] == [False, True]:
                # print(hbcolRED + "X", end=colRESTORE)
                print(hcolBLUE+ "X", end=colRESTORE)
            elif domains[(x, y)] == [True, False]:
                # print(["", colBLUE, colGREEN, colYELLOW, "", "", "", "", "", hbcolGRAY][hints[y, x]], end="")
                print(["", colBLUE, colGREEN, colYELLOW, "", "", "", "", "", hcolBLUE][hints[y, x]], end="")
                print(hints[y, x], end=colRESTORE)
            else:
                print(celRED + "Q", end=colRESTORE)
        print()

# each entry in the domains dict holds a list representing the domain for a single variable. an item's position in the list indicates the item (e.g. mine, flag label) and it's value (True, False) represents whether it's still present in the domain or if it's been eliminated.
domains = {}

# an arbitrary constraint program has many variables.. ours mainly has cells.
# we're treading carefully to not assume cells == variables.. so we can have variables besides cells.
# this is why we're adding cells seperately from domain
for y, row in enumerate(hints):
    for x, cell in enumerate(row):
        domains[(x, y)] = [True, True] # IMPLICIT labels: position 0 for "empty", position 1 for "mine". if True then the coresponding label is still in the domain.
        # HACK: bounds of variable domains are not recorded.. I'm expecting myself to know and remember what domain members corespond to what.
        # right now, that's just cells, which is simple.






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

def arrangementToString(arrangement):
    return "".join(["1" if val else "_" for val in arrangement])

############### CONSTRAINTS
# at a high-level, we follow the simple constraint:
# for every hint, the sum of mines in its neighbours is equal to the hint number.

# for use with GAC, RAC2, RAC3,
# we further break this down into the possible combinations of mines e.g.
# for a hint of 1, there is either 1 mine top-left and no mine elsewhere, or 1 mine top and no mine elsewhere, or 1 mine top-right and no mine elsewhere, etc.
# with increasing combinations for more mines.

# print("arrangements test")
# testSpot = spot_pick([False]*8, 0, 7)
# for arr in testSpot:
#     print(arrangementToString(arr))

# for i in range(9):
#     testSpot = spot_pick([False]*8, 0, i)
#     print("hints:", i, "positions:", len(testSpot))

print("building constraints")

constraints = [] # WARN@ "constraints" here actually means "constraint domains". each entry in this list corresponds to a single constraint. each entry/constraint is a list, of all the different possible acceptable assignments.
variableToConstraints = {}
constraintsToVariables = {}

for y in range(hints.shape[0]):
    for x in range(hints.shape[1]):
        hintCount = hints[y][x]

        print(f"at pos ({x}, {y}), next constraint is {len(constraints)}")

        if (hintCount == 9): # hintCount==9 states a covered cell, so we dont constrain its neighbours because we dont have a "hint" for that cell.
            continue


        # above check didnt skip this cell, so it's a hint cell.
        # for a hint cell, our FIRST CONSTRAINT IS THAT THE CELL IS OPEN.
        constraintID = len(constraints)
        # record the mapping from the new constraint to the variables it influences (in this cases just (x, y))
        constraintsToVariables[constraintID] = [(x, y)]
        # record the constraint as being one that influences this variable
        variableToConstraints[(x, y)] = variableToConstraints.get((x, y), []) + [constraintID] # WARN: creating a new array each time..
        # record the actual constraint
        constraintImpacts = [{(x, y): 0}]
        constraints.append(constraintImpacts)

        domains[(x, y)] = [True, False]

        # secondly, we constraint that the sum of neighbours is equal to the hint number... all of that is done below. note some ramblings are within old context. enjoy sifting comments :)


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

        constraintID = len(constraints) # get the "ID" of the new constraint

        # this only needs to dictate the logic of the constraint.. i.e. what it does with its variables and how it gets validated.
        # since we're operating with only a single constraint (lucky!) we can simplify the constraint logic to just the set of valid arrangements
        # instead of arbitrary logic.

        relevantVariables = [] # temporary list with all the variables this constraint influences
        for y2 in range(y-1, y+2):
            for x2 in range(x-1, x+2):
                if (y2 != y or x2 != x) and y2 >= 0 and y2 < hints.shape[0] and x2 >= 0 and x2 < hints.shape[1]: # if the neighbour is within bounds
                    relevantVariables.append((x2, y2))
                # else:
                #     print("discarded neighbor", x2, y2, "for", x, y, f"..see {y2} != {y} and {x2} != {x} and {y2} >= 0 and {y2} < {hints.shape[0]} and {x2} >= 0 and {x2} < {hints.shape[1]}")
        # print("releveant variables (Neighbours) at", x, y, "are", relevantVariables)

        # record the mapping from this new constraint to all of the variables it influences
        constraintsToVariables[constraintID] = relevantVariables

        # for every variable influenced.. record this constraint as being one that influences the variable.
        for var in relevantVariables: variableToConstraints[var] = variableToConstraints.get(var, []) + [constraintID] # WARN: creating a new array each time..


        # ^ we recorded the mappings, but for the constraint to actually "exist" we need to initialise the "domain" of the constraint, similary to the variables.
        # I define the "domain" of a constraint being the enumeration of every possible label set (over relevant variables) which still satisfies it.

        # now we need to make a unique constraint for every combination of mines among the neighbours.
        enumerationBlank = [False]*len(relevantVariables) # start with a blank enumeration
        enumerations = []

        if hintCount > 0: enumerations = spot_pick(enumerationBlank, 0, hintCount)
        else: enumerations = [enumerationBlank] # a hint of 0 means all neighbours are forced to be open
        # print("enumerations at", x, y, "with count", hintCount, "are", enumerations)

        constraintImpacts = []
        for enumer in enumerations:
            cons = {} # mapping from variable IDs (cell x,y in my case) to the acceptable label. if multiple labels are acceptable, then there will be another enumeration.
            for requiredMine, relVar in zip(enumer, relevantVariables):
                cons[relVar] = 1 if requiredMine else 0 # NOTE: 1 and 0 here are IDs for LABELS. 0 is the ID for label "empty", 1 is the ID for label "mine"
            constraintImpacts.append(cons)


        constraints.append(constraintImpacts)

print()

print("raw domains:")
print(domains) # SHOULD CHANGE, but only upon the discovery of a label that is never possible.
print("_____________________")
print("rendered domains:")
renderDomains(domains)
print("_____________________")

print("raw constraints:")
# print(constraints) # SHOULD CHANGE, but only in response to a domain being changed.
for const in constraints: print(const)
print("_____________________")

print("vars to constraints:")
# print(variableToConstraints) # should never change after the inital constraint expansion..
for item in variableToConstraints: print(item, ":", variableToConstraints[item])
print("_____________________")

print("constraints to vars:")
# print(constraintsToVariables) # should never change after the initial constraint expansion..
for item in constraintsToVariables: print(item, ":", constraintsToVariables[item])
print("_____________________")

# now the model is done and set up...
# time to move on to "solving", first via GAC.

################ GAC

# todo is a list of variables that are potentially not arc consistent w.r.t. to a constraint.
todo = set()

# todo is (initially) a list of every pairing between a variable and a constraint that acts upon it.
for variable in domains: # remember that domains is dictionary between {variable: domainSet}
    if variable in variableToConstraints: # if the variable has a constraint (unconstrained variables currenly comprise cells that arent surrounded by any hints)
        for constraint in variableToConstraints[variable]:
            todo.add((variable, constraint))

print("_"*50)
print("TODO:")
print(todo)

def consistencyCheck(testableLabel, victimVariable, supportVariables, constraint):
    # print(f"conistency check on {testableLabel=}, {victimVariable=}, {supportVariables=}, {constraint=}")
    for acceptedAssignment in constraints[constraint]:
        # print("checking assignment", acceptedAssignment)
        if acceptedAssignment[victimVariable] != testableLabel:
            continue

        # check that the current assignment is valid under the current restricted domain
        supportable = True
        for supVar in supportVariables:
            requiredLabel = acceptedAssignment[supVar] # get the label that this assignment requires for this variable
            if not domains[supVar][requiredLabel]:
                supportable = False
                # print(f"not supportable since {supVar} doesnt have label {requiredLabel}")
                break

        if supportable: return True

    return False;

# exit()

newDomains = copy.deepcopy(domains)

# ATTEMPT ONE: implementing algorithm from https://artint.info/3e/html/ArtInt3e.Ch4.S3.html
while len(todo) > 0: # line 3
    # line 4
    todoable = todo.pop()
    todoX, todoc = todoable

    #line 5
    todoYs = [otherVar for otherVar in constraintsToVariables[todoc] if otherVar != todoX]
    # print("for", todoable, "we get Ys", todoYs)

    # line 6 and 7
    """
    for this step we need all the labels on todoX which have a support across variables todoYs,
    according to constraint todoc.
    """
    acceptedLabels = [] # NOTE: variable naming: "accepted labels" actually just means variable domains re-adusted according to what labels are arc consistent
    for xLabelI in range(len(domains[todoX])):
        if domains[todoX][xLabelI] and consistencyCheck(xLabelI, todoX, todoYs, todoc): # if the label is still enabled in the domain, and the label meets the consistency check..
            acceptedLabels.append(True) # record the variable as supported
        else:
            acceptedLabels.append(False) # record the label as not supported

    # line 8
    # if acceptedLabels != domains[todoX]:
    if acceptedLabels != domains[todoX] and acceptedLabels != newDomains[todoX]:
        # line 9
        """
        for this step we need every variable Z such that Z is connected to X as a neighbour through a constraint c'
        ^ subject to c' != c and Z != X
        """
        for cP in variableToConstraints[todoX]: # for each constraint connected to X
            for todoY in constraintsToVariables[cP]: # for each variable connected to that constraint
                if todoY != todoX and cP != todoc:
                    todo.add((todoY, cP))

        # line 10
        # domains[todoX] = acceptedLabels
        newDomains[todoX] = acceptedLabels

        print(f"domains changed! on {todoX}: {domains[todoX]} went to {acceptedLabels}")
        print("new domains:")
        # print(domains)
        # renderDomains(domains)
        renderDomains(newDomains)
        print()

    # print("new todo:")
    # print(todo)
    # print()
    # print()
domains = newDomains
print("domains after one attempt:")
renderDomains(domains)



exit()
########################## AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa

# todo is a list of variables that are potentially not arc consistent w.r.t. to a constraint.
todo = set()

# todo is (initially) a list of every pairing between a variable and a constraint that acts upon it.
for variable in domains: # remember that domains is dictionary between {variable: domainSet}
    if variable in variableToConstraints: # if the variable has a constraint (unconstrained variables currenly comprise cells that arent surrounded by any hints)
        for constraint in variableToConstraints[variable]:
            todo.add((variable, constraint))

newDomains = copy.deepcopy(domains)

# ATTEMPT ONE: implementing algorithm from https://artint.info/3e/html/ArtInt3e.Ch4.S3.html
while len(todo) > 0: # line 3
    # line 4
    todoable = todo.pop()
    todoX, todoc = todoable

    #line 5
    todoYs = [otherVar for otherVar in constraintsToVariables[todoc] if otherVar != todoX]
    # print("for", todoable, "we get Ys", todoYs)

    # line 6 and 7
    """
    for this step we need all the labels on todoX which have a support across variables todoYs,
    according to constraint todoc.
    """
    acceptedLabels = [] # NOTE: variable naming: "accepted labels" actually just means variable domains re-adusted according to what labels are arc consistent
    for xLabelI in range(len(domains[todoX])):
        if domains[todoX][xLabelI] and consistencyCheck(xLabelI, todoX, todoYs, todoc): # if the label is still enabled in the domain, and the label meets the consistency check..
            acceptedLabels.append(True) # record the variable as supported
        else:
            acceptedLabels.append(False) # record the label as not supported

    # line 8
    # if acceptedLabels != domains[todoX]:
    if acceptedLabels != domains[todoX] and acceptedLabels != newDomains[todoX]:
        # line 9
        """
        for this step we need every variable Z such that Z is connected to X as a neighbour through a constraint c'
        ^ subject to c' != c and Z != X
        """
        for cP in variableToConstraints[todoX]: # for each constraint connected to X
            for todoY in constraintsToVariables[cP]: # for each variable connected to that constraint
                if todoY != todoX and cP != todoc:
                    todo.add((todoY, cP))

        # line 10
        # domains[todoX] = acceptedLabels
        newDomains[todoX] = acceptedLabels

        print(f"domains changed! on {todoX}: {domains[todoX]} went to {acceptedLabels}")
        print("new domains:")
        # print(domains)
        # renderDomains(domains)
        renderDomains(newDomains)
        print()

    # print("new todo:")
    # print(todo)
    # print()
    # print()
domains = newDomains
print("domains after TWO attempt:")
renderDomains(domains)




"""
remember - AC3,4 only operates over binary constraints.
we've implemented this model directly with multi-varaible constraints (specifically, constraints with 8 variables, each of its neighbours)

so for any first start we need to go directly into generalized arc consistency.
"""

# GAC pseudocode translation attempt
""" MAIN ALGORITHM:

pick a cell, and pick a label on that cell e.g. cell is mine:
    for each constraint using that cell that supports the chosen label (i.e. supports that cell is mine):
        for each alternative labeling set within the context of that constraint
        ^^^ i.e. with that mine marked, consider all the other possible combinations (<-- for neighbours..) where those combinations also have the same cell marked as a mine
            for each cell and labelling in the combination..
                

"""

""" SETUP ALGORITHM (for some reason the paper explains the set up after the core..
for each node:
    1. initialise the node's labels (i.e. mine or not mine)
    2. and then..
    for each constraint involved with the node:
        for each node involved in this constraint:
            for each label that node can take:
                1. initialise an empty list
                2. for each possible p-uple for the aforementioned constraint, with the aforementioned node label..
                    create an arbitrary node N, in the collection of p-uples with this specific node,label,relation S_jbr


for each cell c1
    initialise labels with mine, noMine
    for each constraint r1 on the cell c1:
        for each cell c2 constrainted by r1:
            1. initialise empty list
            2. for each p-uple in the input:
                1. let r2 be the corresponding constraint to the puple
                2. for each entry (cell, label) in the puple:
                    

"""
