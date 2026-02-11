import numpy as np
import copy

import inputHandler
import solverAlgs
import minesweeperModel

hints = inputHandler.get_test_input() # NOTE: "hints" here also includes hidden cells, indicated by a value of 9

print("hints:")
print(hints)
print()

print("building domains")
domains = minesweeperModel.create_domains(hints)

print("building constraints")
constraints = minesweeperModel.build_constraints(hints, domains)


print()

print("raw domains:")
print(domains) # SHOULD CHANGE, but only upon the discovery of a label that is never possible.
print("_____________________")
print("rendered domains:")
minesweeperModel.renderDomains(domains, hints)
print("_____________________")

print("raw constraints:")
# print(constraints) # SHOULD CHANGE, but only in response to a domain being changed.
for const in constraints: print(const)
print("_____________________")

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
print(f"starting domains:")
minesweeperModel.phaseRenderDomains(domainsArr, hints)


for i in range(4):
    # domains = solverAlgs.generalizedArcConsistency(domainsArr[-1], constraints, hints)
    # domains = solverAlgs.relationalArcConsistency(domainsArr[-1], constraints, hints)
    if i == 0: domains = solverAlgs.relationalArcConsistency(domainsArr[0], constraints, rac_i=1, rac_m=1)
    elif i == 1: domains = solverAlgs.relationalArcConsistency(domainsArr[0], constraints, rac_i=1, rac_m=2)
    elif i == 2: domains = solverAlgs.relationalArcConsistency(domainsArr[0], constraints, rac_i=1, rac_m=3)
    else: domains = solverAlgs.relationalArcConsistency(domainsArr[0], constraints, rac_i=1, rac_m=4)

    domainsArr.append(domains)
    print(f"domains after {i+1} attempts:")
    # minesweeperModel.renderDomains(domains, hints)
    minesweeperModel.phaseRenderDomains(domainsArr, hints)
    print()
