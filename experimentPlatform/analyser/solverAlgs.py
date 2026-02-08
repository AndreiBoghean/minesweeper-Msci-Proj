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

def relationalArcConsistency(domains, constraints, variableToConstraints, constraintsToVariables, hints, i=1, m=1):
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


    # ATTEMPT TWO: I'm now modifying attempt ONE to look like Rina Dechter's specification of RELATIONAL-CONSISTENCT(R, i, m) as outlined in their constraint processing textbook.
    # whenever I'm referencing that implementation, I'll simply say RC(i, m) or something along those lines

    # first we build "m relations R_{S_1}, ..., R_{S_m} \in Q" as specified by line 3 of RC
    relations_masks = minesweeperModel.spot_pick([False]*len(constraints), 0, m) # out of all relations, pick m different relations. (0 just means start from the leftmost.. just there since this is a recursive algorithm)
    relations_todos = [[i for i in range(len(constraints)) if relation_mask[i]] for relation_mask in relations_masks] # ayys is a set containing every subset A of size i in the Rs selection (i.e. it's the second half of line 3 of RC)

    for relation_selection in relations_todos: # finally carry out line 3 part 1.. that is.. "for every m relations R_S_{1}, ..., R_S_{m} \in Q ... do other stuff"

        # now, for line 3 part 2,
        # we need to build a subset A of size i, subject to "A \subseteq foldl_union[S_j for x in range(m)]"
        # my logical anchor is that, for i=1 m=1, this simply goes to todoables[0] (where todoables should only be one item since m=1)

        all_relation_variables = []
        for relation in relation_selection:
            all_relation_variables.extend(constraintsToVariables[relation])
        all_relation_variables = list(set(all_relation_variables))

        relVars_masks = minesweeperModel.spot_pick([False]*len(all_relation_variables), 0, i) # out of the m options in the current relation selection, pick i spots. (0 just means start from the leftmost.. just there since this is a recursive algorithm)
        ayys = [[var for i, var in enumerate(all_relation_variables) if relVars_mask[i]] for relVars_mask in relVars_masks] # ayys is a set containing every subset A of size i in the Rs selection (i.e. it's the second half of line 3 of RC)
        # ^ reminder number 4 of the fact that ayys is the set of all subsets A of size i containing stuff. idk. just see line 3 part 2 from the book.

        for ayy in ayys:
            # technically, with i=1 and m=1, if we run this algorithm like we were doing before with GAC,
            # then at this point we should be given a single todox and todoc, much like our GAC attempt.

            todoX = ayy[0]
            todoc = relation_selection[0]

            #GAC line 5
            # this line calculates the inverse of A w.r.t. 
            todoYs = [otherVar for otherVar in constraintsToVariables[todoc] if otherVar != todoX]
            # print("for", todoables, "we get Ys", todoYs)

            # GAC line 6 and 7
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

            # GAC line 8
            # if acceptedLabels != domains[todoX]:
            if acceptedLabels != domains[todoX] and acceptedLabels != newDomains[todoX]: # modification to the original algorithm: check the "discovery" we just made hasnt already been made (it it had been, then it'd already be in newDomains)
                # GAC line 9
                """
                for this step we need every variable Z such that Z is connected to X as a neighbour through a constraint c'
                ^ subject to c' != c and Z != X
                """
                # TODO: port over this optimisation.
                # for cP in variableToConstraints[todoX]: # for each constraint connected to X
                #     for todoY in constraintsToVariables[cP]: # for each variable connected to that constraint
                #         if todoY != todoX and cP != todoc:
                #             todo.add((todoY, cP))

                # GAC line 10
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
