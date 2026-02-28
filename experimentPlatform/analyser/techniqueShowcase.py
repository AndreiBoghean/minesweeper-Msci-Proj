import numpy as np
import copy

import inputHandler
import solverAlgs
import minesweeperModel

techniques = {
        "basic pattern B1 and B2": [
            [0, 0, 1, 9, 9],
            [0, 0, 2, 9, 9],
            [0, 0, 3, 9, 9],
            [1, 1, 2, 9, 9],
            [9, 9, 9, 9, 9],
        ],
        "basic pattern 1-1": [
            [9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9],
            [1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ],
        "basic pattern 1-1+": [
            [9, 9, 9, 9, 9, 9],
            [9, 2, 9, 9, 9, 9],
            [1, 1, 1, 1, 9, 9],
            [0, 0, 0, 1, 9, 9],
            [0, 0, 0, 1, 9, 9],
        ],
        "basic pattern 1-2": [
            [9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9],
            [1, 2, 1, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ],
        "basic pattern 1-2+": [
            [9, 9, 9, 9, 9, 9],
            [9, 2, 9, 9, 9, 9],
            [1, 1, 1, 4, 9, 9],
            [0, 0, 0, 2, 9, 9],
            [0, 0, 0, 1, 9, 9],
        ],
        "basic pattern 1-2C": [
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [9, 3, 1, 2, 3, 9],
            [9, 2, 0, 0, 2, 9],
            [9, 2, 0, 0, 2, 9],
        ],
        "basic pattern 1-2C+": [
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [1, 1, 1, 4, 9, 9],
            [0, 0, 0, 2, 9, 9],
            [0, 0, 0, 1, 9, 9],
        ],
        "basic pattern 1-2-1": [
            [9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9],
            [3, 1, 2, 1, 4],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ],
        "basic pattern 1-2-2-1": [
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [3, 1, 2, 2, 1, 3],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ],

        "reduction pattern 1-1R": [
            [0, 1, 9, 9, 9],
            [1, 2, 9, 9, 9],
            [9, 2, 9, 9, 9],
            [3, 4, 9, 9, 9],
            [9, 9, 2, 2, 9],
        ],
        "reduction pattern 1-2R": [
            [3, 2, 1, 1, 2],
            [9, 9, 1, 1, 9],
            [9, 4, 2, 3, 3],
            [9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9],
        ],
        "reduction pattern 1-2-1R": [
            [9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9],
            [1, 2, 3, 2, 1],
            [0, 1, 9, 1, 0],
            [0, 1, 1, 1, 0],
        ],

        "high complexity 1-3-1 corner": [
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [1, 1, 1, 3, 9, 9],
            [0, 0, 0, 1, 9, 9],
            [0, 0, 0, 1, 9, 9],
            [0, 0, 0, 1, 9, 9],
        ],
        "high complexity 2-2-2 corner": [
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [2, 2, 2, 2, 9, 9],
            [0, 0, 0, 2, 9, 9],
            [0, 0, 0, 2, 9, 9],
            [0, 0, 0, 2, 9, 9],
        ],
        "high complexity 1>2<1": [
            [9, 9, 9, 9, 9],
            [3, 1, 1, 9, 9],
            [3, 1, 1, 9, 9],
            [9, 1, 9, 9, 9],
            [3, 1, 2, 9, 9],
            [0, 0, 1, 9, 9],
            [0, 0, 1, 9, 9],
            [0, 0, 3, 9, 9],
        ],
        "high complexity T-pattern": [
            [9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9],
            [9, 4, 3, 2, 9, 9],
            [9, 9, 1, 9, 9, 9],
            [1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0],
        ],
        "high complexity dependency chain": [
            [2, 2, 9, 9, 9],
            [9, 3, 9, 9, 9],
            [2, 9, 9, 9, 9],
            [1, 9, 2, 9, 9],
            [1, 1, 2, 9, 9],
            [1, 9, 2, 9, 9],
            [1, 9, 2, 9, 9],
            [1, 1, 2, 9, 9],
            [2, 9, 2, 9, 9],
            [9, 9, 9, 9, 9],
            [9, 9, 2, 1, 2],
        ],
        "doughnut": [
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
            [9, 9, 9, 2, 2, 2, 2, 9, 9, 9],
            [9, 9, 9, 2, 0, 0, 2, 9, 9, 9],
            [9, 9, 9, 2, 0, 0, 2, 9, 9, 9],
            [9, 9, 9, 2, 2, 2, 2, 9, 9, 9],
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        ],
}
for t in techniques: techniques[t] = np.array(techniques[t]) # too lazy to put np.array() on each array item

for title, hints in techniques.items():
    if "doughnut" not in title: continue

    print(f"analising technique", title)

    debug_prints = False
    if debug_prints: print("building domains")
    domains = minesweeperModel.create_domains(hints)

    if debug_prints: print("building constraints")
    constraints = minesweeperModel.build_constraints(hints, domains)


    if debug_prints: print()

    if debug_prints: print("raw domains:")
    if debug_prints: print(domains) # SHOULD CHANGE, but only upon the discovery of a label that is never possible.
    if debug_prints: print("_____________________")
    if debug_prints: print("rendered domains:")
    if debug_prints:minesweeperModel.renderDomains(domains, hints)
    if debug_prints: print("_____________________")

    if debug_prints: print("raw constraints:")
    # print(constraints) # SHOULD CHANGE, but only in response to a domain being changed.
    # for const in constraints: print(const)
    if debug_prints: print("_____________________")

    # print("vars to constraints:")
    # # print(variableToConstraints) # should never change after the inital constraint expansion..
    # for item in variableToConstraints: print(item, ":", variableToConstraints[item])
    # print("_____________________")
    # 
    # print("constraints to vars:")
    # # print(constraintsToVariables) # should never change after the initial constraint expansion..
    # for item in constraintsToVariables: print(item, ":", constraintsToVariables[item])
    # print("_____________________")

    # now the model is done and set up...
    # time to move on to "solving", first via GAC.

    ################ GAC

    domainsArr = [domains]

    for i in range(5):
        domains = domainsArr[0]
        constraints = minesweeperModel.build_constraints(hints, domains)
        if i == 0: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=1)
        elif i == 1: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=2)
        elif i == 2: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=3)
        elif i == 3: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=4)
        elif i == 4: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=5)
        else: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=6)

        domainsArr.append(domains)

    print(f"domains after {i+1} attempts:")
    # minesweeperModel.renderDomains(domains, hints)
    minesweeperModel.phaseRenderDomains(domainsArr, hints)
    print()
