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

############ TODO: LOOK DOWN HERE VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV

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
        nAyys = [[var for i, var in enumerate(all_relation_variables) if not relVars_mask[i]] for relVars_mask in relVars_masks] # simply the inverse of the As
        # ^ reminder number 4 of the fact that ayys is the set of all subsets A of size i containing stuff. idk. just see line 3 part 2 from the book.

        for ayy, nayy in zip(ayys, nAyys):
            # technically, with i=1 and m=1, if we run this algorithm like we were doing before with GAC,
            # then at this point we should be given a single todox and todoc, much like our GAC attempt.

            # todoX = ayy[0]
            # todoc = relation_selection[0]

            #GAC line 5
            # this line calculates the inverse of A w.r.t. 
            # todoYs = [otherVar for otherVar in constraintsToVariables[todoc] if otherVar != todoX]
            # todoYs = sorted(todoYs, key=lambda a: (a[0]+a[1]))
            # nayy = sorted(todoYs, key=lambda a: (a[0]+a[1]))
            # print(f"{todoYs=}")
            # print(f"{nayy=}")
            # print(f"{str(todoYs) == str(nayy)=}")
            # if (str(todoYs) != str(nayy)):
            #     print("WHYYYYYY!!!!")
            #     exit()
            # print()

            # within RAC, GAC's todoYs is equiv to our ¬A
            todoYs = nayy

            # basically: for each variable in set A, and for each accepted label,
            # try it within the context of the wider set {R_S_{1}, ..., R_S_{m}}
            # and reject the label assignmrnt from A if it doesnt agree with the contex.

            # FIRSTLY, I build the NATURAL JOIN of all relevant relations R_S_{1}, ..., R_S_{m}.
            # to do this, I collect all the relevant variables into a pool,
            # and compute every combination of assignments to those variables.

            # SECONDLY, I iterate over every variable in the pool, and look at all the constraints on it.
            # for each of that constraint, we mask the constraint's variables with our variable set,
            # and ask it whether it accepts the current assignment we#re considering.
            #     ^ remember, this is happening for every constraint on every variable :(


            # actually scratch all of that. natural join, with no columns in common, degrades to the cartesean product.
            # for ...
            def inner_join(R1, R2):
                # in theory, a relation is a list of accepted assignments over its relevant variables.
                # "relevant variables" is not actually encoded within the variable.. the variable is just an ID,
                # and the relation variables and allowed assignments are given under "constraintToVariables" and "constraints".

                # the purpose of this inner join is for working-version relations, that get built up across multiple relations.
                # so, how to create a working version relation representation?
                # must remember the variables it operates over.

                R1_domains = copy.deepcopy(constraints[R1]) # a list of assignment sets
                R1_vars = copy.deepcopy(constraintsToVariables[R1]) # a list of positions on the board
                R2_domains = copy.deepcopy(constraints[R2]) # a list of assignment sets
                R2_vars = copy.deepcopy(constraintsToVariables[R2]) # a list of positions on the board

                # print(f"{R1_domains=}")
                # print(f"{R1_vars=}")
                # print(f"{R2_domains=}")
                # print(f"{R2_vars=}")


                new_domains = []
                new_vars = copy.deepcopy(R1_vars)
                for v in R2_vars:
                    if v not in new_vars:
                        new_vars.append(v)

                mergeable_vars = []
                for i, R1_var in enumerate(R1_vars):
                    for j, R2_var in enumerate(R2_vars):
                        if (R2_var == R1_var):
                            mergeable_vars.append((i, j)) # if the 2nd variable is the same, mark it for skipping

                # ^ note that we're assuming R1 vars is fully present in mergeable_vars, and duplicates are only dropped from R2 instead of R1 if they exist.
                # this assumption is taken because domains/vars associations are parallel lists, and require indices to match.

                for R1_assignment in R1_domains:
                    for R2_assignment in R2_domains:

                        new_assignment = {}
                        drop_domain = False;

                        for overlap in mergeable_vars:
                            common_var_1, common_var_2 = R1_vars[overlap[0]], R2_vars[overlap[1]]
                            # print(f"is R1_vars[{common_var_1=}]={common_var_1} != R2_vars[{common_var_2=}]={common_var_2}")
                            if R1_assignment[common_var_1] != R2_assignment[common_var_2]:
                                drop_domain = True
                                break

                        if drop_domain:
                            continue


                        # start with the first relation
                        for i, R1_var in enumerate(R1_vars):
                            new_assignment[R1_var] = R1_assignment[R1_var]

                        # then the second relation, but exclude columns already present (i.e variables that were added when part of R1)
                        for i, R2_var in enumerate(R2_vars):
                            new_assignment[R2_var] = R2_assignment[R2_var]

                        # # start with the first relation
                        # for i, R1_var in enumerate(R1_vars):
                        #     new_domain.append(R1_assignment[i])

                        # # then the second relation, but exclude columns already present (i.e variables that were added when part of R1)
                        # for i, R2_var in enumerate(R2_vars):
                        #     if filter(mergeable_vars, key=lambda t: t[1] == i) != []: # if i isnt unique, skip it.
                        #         continue
                        # 
                        #     new_domain.append(R2_assignment[i])

                        new_domains.append(new_assignment)

                return new_domains, new_vars

            # TODO: inner join over all relations
            # relations_natJoin = copy.deepcopy(all_relation_variables)
            # for support in R_S_{1}:
            #     for variable in support:


            for todoX, todoc in zip(ayy, relation_selection):

                # # NOTEL sanity check: validating that inner join A, A = A
                # current_constrs = constraints[todoc]
                # current_constr_vars = constraintsToVariables[todoc]
                # new_constrs, new_constr_vars = inner_join(todoc, todoc)

                # print(f"old constrs: {current_constrs}")
                # print(f"new constrs: {new_constrs}")
                # print(f"old constrs vars: {current_constr_vars}")
                # print(f"new constrs vars: {new_constr_vars}")
                # print()

                # if (current_constrs != new_constrs):
                #     print("PANIK with constrs")
                #     exit()

                # if (current_constr_vars != new_constr_vars):
                #     print("PANIK with constrs_vars")
                #     exit()

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
