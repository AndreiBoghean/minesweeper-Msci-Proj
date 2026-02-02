import copy

import minesweeperModel

def generalizedArcConsistency(domains, constraints, variableToConstraints, constraintsToVariables, hints):
    # helper func
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


    newDomains = copy.deepcopy(domains) # make sure we dont modify the original domains.. otherwise we accidentally solve too much.

    # todo is a list of variables that are potentially not arc consistent w.r.t. to a constraint.
    todo = set()

    # todo is (initially) a list of every pairing between a variable and a constraint that acts upon it.
    for variable in domains: # remember that domains is dictionary between {variable: domainSet}
        if variable in variableToConstraints: # if the variable has a constraint (unconstrained variables currenly comprise cells that arent surrounded by any hints)
            for constraint in variableToConstraints[variable]:
                todo.add((variable, constraint))

    # print("_"*50)
    # print("TODO:")
    # print(todo)

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
        if acceptedLabels != domains[todoX] and acceptedLabels != newDomains[todoX]: # modification to the original algorithm: check the "discovery" we just made hasnt already been made (it it had been, then it'd already be in newDomains)
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

            # print(f"domains changed! on {todoX}: {domains[todoX]} went to {acceptedLabels}")
            # print("new domains:")
            # print(domains)
            # minesweeperModel.renderDomains(newDomains, hints)
            # print()

        # print("new todo:")
        # print(todo)
        # print()
        # print()

    return newDomains
















############# OLD RAMBLINGS WE BURRY AND FORGET:



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
