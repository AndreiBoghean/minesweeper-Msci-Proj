import inputStatisticaler
import averageDifficultyPOC
import inputHelper
import inputHandler
import cellReward

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# import the solve time data
_, _, _, solveTime_avgs = inputStatisticaler.process_box_solve_time_per_field()

# import the difficulty data
difficulty_data = []
testFields = list(inputHelper.seed_3bv_lookup.values())
entries = inputHandler.get_all_database_content()
for testField in testFields:
    difficulty_grid = averageDifficultyPOC.compute_cell_difficulties(testField, entries, render=False, debug=False)
    difficulty_data.append(np.sum(difficulty_grid))

# import cellReward data
reward_data = []
for testField in testFields:
    reward_grid  = cellReward.compute_cell_rewards(testField, entries, render=False)
    reward_data.append(np.sum(reward_grid))

# third, check their corelation<D-y>.

data = {
    "threeBVs": testFields,
    "timeSolve": solveTime_avgs,
    "difficulty": difficulty_data,
    "cellReward": reward_data,
}

df = pd.DataFrame(data)
print(df.round(2))

def shortCor(da, db):
    correlation = df[da].corr(df[db])
    # print(f"({da}, {db}) Pearson Correlation Coefficient: {correlation}")

    print(f"{correlation}", end=", ")

    pear = pearsonr(df[da], df[db])
    # print(f"{pear.statistic=} {pear.pvalue=}, signif:{pear.pvalue <= 0.05}")
    if pear.pvalue > 0.05:
        print("WARNING! CORRELATION NOT SIGNIFICANT:")
        print(f"{pear.statistic=} {pear.pvalue=}, signif:{pear.pvalue <= 0.05}")

for key in data:
    print(key, end=", ")
print()

for key1 in data:
    # print(f"\n{key1} stuff:")
    for key2 in data:
        # if key1 == key2: continue
        shortCor(key1, key2)
    print()

df.plot()
plt.show()

exit()
plt.scatter(df["solveTime"], df["diffData"])
plt.title("solveTime vs diffData")
plt.xlabel("solveTime")
plt.ylabel("diffData")
plt.grid()
plt.show()
