import copy

def generalizedArcConsistency(domains, constraints, variableToConstraints, constraintsToVariables, hints):
    # helper func
    def GAC_consistencyCheck(testableLabel, victimVariable, supportVariables, constraint):
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
            if domains[todoX][xLabelI] and GAC_consistencyCheck(xLabelI, todoX, todoYs, todoc): # if the label is still enabled in the domain, and the label meets the consistency check..
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
