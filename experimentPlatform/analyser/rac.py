import copy

import minesweeperModel
import datetime

def relationalArcConsistency(domains, constraints, rac_i=1, rac_m=1):
    # helper functions
    def RAC_consistencyCheck(victimVariables, constraint_domains):
        # reminder: this should just do R_A \union all_relation_domains.
        
        # to do that, we filter constraint_domains down to A.
        
        # and then, for each valid assignment to variables A,
        # we check it's permitted by the filtered constraint_domains

        # we then return only the permitted assignments, in the form of a constraint.

        # for domain1 in A_1:
        #     for domain2 in A_2:
        #         if domain1, domain2 is not in constraint_domains:
        #             remove domain1, domain2 from victimVars relation


        # print(f"conistency check on {testableLabel=}, {victimVariable=}, {supportVariables=}, {constraint=}")
        for domain in constraint_domains:
            for victimVariable in victimVariables:
                demanded_label = domain[victimVariable]
                if domains[victimVariable][demanded_label]: # if the requested label is present in the domain..
                    continue
                else:
                    return domain # return the no-good domain

        return []

    def old_consistencyCheck(testableLabel, victimVariable, supportVariables, relevant_constraints):
        # print(f"conistency check on {testableLabel=}, {victimVariable=}, {supportVariables=}, {constraint=}")
        for acceptedAssignment in relevant_constraints:
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

    def inner_join(R1, R2):
        R1_domains, R1_vars = R1
        R2_domains, R2_vars = R2

        # in theory, a relation is a list of accepted assignments over its relevant variables.
        # "relevant variables" is not actually encoded within the variable.. the variable is just an ID,
        # and the relation variables and allowed assignments are given under "constraintToVariables" and "constraints".

        # the purpose of this inner join is for working-version relations, that get built up across multiple relations.
        # so, how to create a working version relation representation?
        # must remember the variables it operates over.

        new_domains = []
        new_vars = set([var for var in R1_vars])
        for v in R2_vars:
            if v not in new_vars:
                new_vars.add(v)

        mergeable_vars = R1_vars & R2_vars

        for R1_assignment in R1_domains:
            for R2_assignment in R2_domains:

                new_assignment = {}
                drop_domain = False;

                for overlapping_var in mergeable_vars:
                    if R1_assignment[overlapping_var] != R2_assignment[overlapping_var]:
                        drop_domain = True
                        break

                if drop_domain:
                    continue

                # start with the first relation
                for R1_var in R1_vars:
                    new_assignment[R1_var] = R1_assignment[R1_var]

                # then the second relation, but exclude columns already present (i.e variables that were added when part of R1)
                for R2_var in R2_vars:
                    new_assignment[R2_var] = R2_assignment[R2_var]

                new_domains.append(new_assignment)

        return new_domains, new_vars

    def foldl(accum, func, consumable):
        if consumable == []: return accum

        new_item = consumable.pop()
        accum = func(accum, new_item)
        return foldl(accum, func, consumable)

    newDomains = copy.deepcopy(domains) # make sure we dont modify the original domains.. otherwise we accidentally solve too much.


    # ATTEMPT TWO: I'm now modifying attempt ONE to look like Rina Dechter's specification of RELATIONAL-CONSISTENCT(R, i, m) as outlined in their constraint processing textbook.
    # whenever I'm referencing that implementation, I'll simply say RC(i, m) or something along those lines

    # first we build "m relations R_{S_1}, ..., R_{S_m} \in Q" as specified by line 3 of RC
    relations_masks = minesweeperModel.spot_pick([False]*len(constraints), 0, rac_m) # out of all relations, pick m different relations. (0 just means start from the leftmost.. just there since this is a recursive algorithm)
    relations_todos = [[i for i in range(len(constraints)) if relation_mask[i]] for relation_mask in relations_masks] # ayys is a set containing every subset A of size i in the Rs selection (i.e. it's the second half of line 3 of RC)
    # for i = None, we take that to mean unbounded, and adapt execution to do RAC{m} instead of RAC{i,m}.
    # all this is means is making i "unbounded", by setting it to (the size of the union thing) minus 1.
    if rac_i == None:
        rac_i = len(relations_masks)-1


    last_print = 0
    rel_progress = -1
    start_time = datetime.datetime.now()
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    for relation_selection in relations_todos: # finally carry out line 3 part 1.. that is.. "for every m relations R_S_{1}, ..., R_S_{m} \in Q ... do other stuff"
        rel_progress += 1

        if (rel_progress-last_print) >= 0.001 * len(relations_todos):
            print(f"RAC i={rac_i} m={rac_m}: {rel_progress}/{len(relations_todos)} = {str(round(rel_progress/len(relations_todos), 5)).ljust(8)} at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (started {start_time_str}) (taking {round((datetime.datetime.now()-start_time).seconds/60, 3)}m)", end="\r")
            last_print = rel_progress

        # # NOTEL sanity check: validating that inner join A, A = A
        # current_constrs = constraints[todoc]
        # current_constr_vars = minesweeperModel.constraintToVariables(constraints, todoc)
        # new_constrs, new_constr_vars = inner_join(todoc, todoc)
        # print(f"old constrs: {current_constrs}\nnew constrs: {new_constrs} \nold constrs vars: {current_constr_vars} \nnew constrs vars: {new_constr_vars}")
        # if (current_constrs != new_constrs OR current_constr_vars != new_constr_vars):
        #     print(f"PANIK with inner join validity {current_constrs != new_constrs=} OR {current_constr_vars != new_constr_vars=}")
        #     exit()

        relation_selection_units = [(constraints[relation_ID], minesweeperModel.constraintToVariables(constraints, relation_ID)) for relation_ID in relation_selection]
        starter_item = relation_selection_units.pop()
        all_relation_domains, all_relation_variables = foldl(starter_item, inner_join, relation_selection_units)


        relVars_masks = minesweeperModel.spot_pick([False]*len(all_relation_variables), 0, rac_i) # out of the m options in the current relation selection, pick i spots. (0 just means start from the leftmost.. just there since this is a recursive algorithm)
        ayys = [[var for i, var in enumerate(all_relation_variables) if relVars_mask[i]] for relVars_mask in relVars_masks] # ayys is a set containing every subset A of size i in the Rs selection (i.e. it's the second half of line 3 of RC)
        nAyys = [[var for i, var in enumerate(all_relation_variables) if not relVars_mask[i]] for relVars_mask in relVars_masks] # simply the inverse of the As
        # ^ reminder number 4 of the fact that ayys is the set of all subsets A of size i containing stuff. idk. just see line 3 part 2 from the book.

        for ayy, nayy in zip(ayys, nAyys): # for each subset A..
            for todoX in ayy:
                # GAC line 6 and 7
                """
                for this step we need all the labels on todoX which have a support across variables nayy,
                according to constraint todoc.
                """
                acceptedLabels = [] # NOTE: variable naming: "accepted labels" actually just means variable domains re-adusted according to what labels are arc consistent
                for xLabelI in range(len(domains[todoX])):
                    if domains[todoX][xLabelI] and old_consistencyCheck(xLabelI, todoX, nayy, all_relation_domains): # if the label is still enabled in the domain, and the label meets the consistency check..
                    # if domains[todoX][xLabelI] and [] == consistencyCheck(ayy, all_relation_domains):
                        acceptedLabels.append(True) # record the variable as supported
                    else:
                        acceptedLabels.append(False) # record the label as not supported


                # new_constraint = []
                # if acceptedLabels[0]: new_constraint.append({todoX: 0})
                # if acceptedLabels[1]: new_constraint.append({todoX: 1})
                # minesweeperModel.insert_constraint(constraints, new_constraint)


                # for var in newDomains: # note that domains keys are variables.. domains is mapping variable->var_domains
                #     accepted_labels = set()
                #     for constraint in minesweeperModel.variableToConstraints(constraints, var):
                #         for assignment in constraints[constraint]:
                #             accepted_labels.add(assignment[var])


                #     for currently_available_label in domains[var]:
                #         if currently_available_label not in accepted_labels:
                #             newDomains[var][currently_available_label] = False
                # continue

                # GAC line 8
                # if acceptedLabels != domains[todoX]:
                if acceptedLabels != domains[todoX] and acceptedLabels != newDomains[todoX]: # modification to the original algorithm: check the "discovery" we just made hasnt already been made (it it had been, then it'd already be in newDomains)
                    # GAC line 9
                    """
                    for this step we need every variable Z such that Z is connected to X as a neighbour through a constraint c'
                    ^ subject to c' != c and Z != X
                    """
                    # TODO: port over this optimisation.
                    # for cP in minesweeperModel.variableToConstraints(constraints, todoX): # for each constraint connected to X
                    #     for todoY in minesweeperModel.constraintToVariables(constraints, cP): # for each variable connected to that constraint
                    #         if todoY != todoX and cP != todoc:
                    #             todo.add((todoY, cP))

                    newDomains[todoX] = acceptedLabels

                # for var in newDomains: # note that domains keys are variables.. domains is mapping variable->var_domains
                #     if var != todoX: continue

                #     accepted_labels = set()
                #     for constraint in minesweeperModel.variableToConstraints(constraints, var):
                #         for assignment in constraints[constraint]:
                #             accepted_labels.add(assignment[var])


                #     for currently_available_label in domains[var]:
                #         if currently_available_label not in accepted_labels:
                #             newDomains[var][currently_available_label] = False


    print() # just to make sure the next print (which is presumably a minesweeper grid) doesnt go onto the carriage return text

    # for var in newDomains: # note that domains keys are variables.. domains is mapping variable->var_domains
    #     accepted_labels = set()
    #     for constraint in minesweeperModel.variableToConstraints(constraints, var):
    #         for assignment in constraints[constraint]:
    #             accepted_labels.add(assignment[var])


    #     for currently_available_label in domains[var]:
    #         if currently_available_label not in accepted_labels:
    #             newDomains[var][currently_available_label] = False

    return newDomains
