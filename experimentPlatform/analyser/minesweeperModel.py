####################################### DOMAINS

def create_domains(hints):
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

    return domains

def renderDomains(domains, hints):
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

    colUNDERLINE = '\033[4m'

    print(colUNDERLINE + " |012345678" + colRESTORE)

    for y, row in enumerate(hints):
        print(f"{y}|", end="")
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
                print(colRED + "Q", end=colRESTORE)
        print()

def phaseRenderDomains(domainsArr, hints):
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
            # presume we're given 4 items in domainsArr: original, algorithm1, algorithm2, algorithm3.
            # anything uncovered by an algorithm will uncover either an open cell (hint==9) or a mine (domain=[False,True]).
            # if something if an open cell, we check what domainArr it was opened in
            # if something is a mine, we check what domainArr it was mined in.
            # and that's how we decide which colour to use.
            options = [hcolGRAY, hcolBLUE, hcolGREEN, hcolYELLOW]
            option = options[0]



            if domainsArr[-1][(x, y)] == [True, True]:
                print(hcolGRAY + "?", end=colRESTORE)

            elif domainsArr[-1][(x, y)] == [False, True]: # SOLVER RELEVANT
                # find the earliest domain iteration where the overvation was true, and use the respective colour.
                for i, domain in enumerate(domainsArr):
                    if domain[(x, y)] == domainsArr[-1][(x, y)]:
                        option = options[i]
                        break

                print(option + "X", end=colRESTORE)

            elif domainsArr[-1][(x, y)] == [True, False]: # SOLVER RELEVANT
                # find the earliest domain iteration where the overvation was true, and use the respective colour.
                for i, domain in enumerate(domainsArr):
                    if hints[y, x]==9 and domain[(x, y)] == domainsArr[-1][(x, y)]:
                        option = options[i]
                        break

                print(["", colBLUE, colGREEN, colYELLOW, "", "", "", "", "", option][hints[y, x]], end="")
                print(hints[y, x], end=colRESTORE)

            else:
                print(celRED + "Q", end=colRESTORE)
        print()

####################################### CONSTRAINTS

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

# print("arrangements test")
# testSpot = spot_pick([False]*8, 0, 7)
# for arr in testSpot:
#     print(arrangementToString(arr))

# for i in range(9):
#     testSpot = spot_pick([False]*8, 0, i)
#     print("hints:", i, "positions:", len(testSpot))


# at a high-level, we follow the simple constraint:
# for every hint, the sum of mines in its neighbours is equal to the hint number.
# for use with GAC, RAC2, RAC3, we further break this down into the possible combinations of mines e.g.
# for a hint of 1, there is either 1 mine top-left and no mine elsewhere, or 1 mine top and no mine elsewhere, or 1 mine top-right and no mine elsewhere, etc.
# with increasing combinations for more mines.
def build_constraints(hints, domains):
    constraints = [] # WARN@ "constraints" here actually means "constraint domains". each entry in this list corresponds to a single constraint. each entry/constraint is a list, of all the different possible acceptable assignments.
    variableToConstraints = {}
    constraintsToVariables = {}

    for y in range(hints.shape[0]):
        for x in range(hints.shape[1]):
            hintCount = hints[y][x]

            # print(f"at pos ({x}, {y}), next constraint is {len(constraints)}")

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

    return constraints, variableToConstraints, constraintsToVariables
