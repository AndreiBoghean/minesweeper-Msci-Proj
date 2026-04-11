import numpy as np
from scipy.signal import convolve2d

import json
import datetime
import os
import sys

import minesweeperModel
import solverAlgs
import inputHelper
import inputHandler

import averageDifficultyPOC
import cellReward

import matplotlib.pyplot as plt


seed_3bv_lookup = {
    "1769089904946": 2,
    "1769089890419": 5,
    "1769089890390": 7,
    "1769089890393": 8,
    "1769089890402": 9,
    "1769089890404": 10,
    "1769089890406": 11,
    "1769089890426": 12,
    "1769089890391": 13,
    "1769089890380": 14,
    "1769089890394": 15,
    "1769089890387": 16,
    "1769089890388": 17,
    "1769089890444": 18,
    "1769089890461": 19,
    "1769089890420": 20,
    "1769089890408": 22,
    "1769089890446": 26,
    "1769089890521": 30,
    "1769089891879": 35,
    "1769089892886": 40,
}
reverse_seed_3bv_lookup = {threebv: seed for seed, threebv in seed_3bv_lookup.items()}

def cell_reward(testFields):
    entries = inputHandler.get_all_database_content()

    rewards = [0] * 41
    for testField in testFields:
        print(f"reward for 3bv:{testField}")
        reward_data = cellReward.compute_cell_rewards(testField, entries, render=True)
        print()

        total_reward = np.sum(reward_data)
        print(f"reward heatmap for 3bv:{testField} (total:{total_reward})")
        rewards[testField] = total_reward


    plt.figure(figsize=(10, 6))
    plt.bar(list(range(41)), rewards, label="stuff", edgecolor="black")
    plt.xlabel("Field (3bv)")
    plt.ylabel("reward")
    plt.title("Distribution of cell reward per field (3bv)")
    unique_fields = [int(x) for x in seed_3bv_lookup.values()]
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.tight_layout()
    plt.legend()
    plt.show(block=True)

def averageDifficulty(testFields):
    entries = inputHandler.get_all_database_content()

    difficulties = [0] * 41
    for testField in testFields:
        print(f"typical difficulties for 3bv:{testField}")
        difficulty_data = averageDifficultyPOC.compute_cell_difficulties(testField, entries, render=True, debug=False)
        print()

        total_difficulty = np.sum(difficulty_data)
        print(f"difficulty heatmap for 3bv:{testField} (total:{total_difficulty})")
        difficulties[testField] = total_difficulty


    plt.figure(figsize=(10, 6))
    plt.bar(list(range(41)), difficulties, label="stuff", edgecolor="black")
    plt.xlabel("Field (3bv)")
    plt.ylabel("difficulty")
    plt.title("Distribution of difficulty per field (3bv)")
    unique_fields = [int(x) for x in seed_3bv_lookup.values()]
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.tight_layout()
    plt.legend()
    plt.show(block=True)

def meanness(testFields):
    entries = inputHandler.get_all_database_content()

    def get_render_context(entries, threebv):
        fullBoard = inputHandler.board_generate(9, 9, 10, reverse_seed_3bv_lookup[threebv])
        fullBoard [fullBoard == -1] = 9 # mask over the mines so they're hidden

        succEntry = [entry for entry in entries if (seed_3bv_lookup[entry["seed"]] == threebv) and entry["successful"]][0]
        thing = inputHandler.load_preprocessed(succEntry)[-1]
        return thing, fullBoard 

    meannesses = [0] * 41

    for testField in testFields:
        entropy_data = cellReward.compute_cell_rewards(testField, entries, render=True, debug=False)
        difficulty_data = averageDifficultyPOC.compute_cell_difficulties(testField, entries, render=True, debug=False)

        entropy_data = entropy_data / np.max(entropy_data)
        difficulty_data = difficulty_data / np.max(difficulty_data)

        meanness_ratios = difficulty_data/(10*(entropy_data+1))
        meanness_ratios = meanness_ratios / np.max(meanness_ratios)

        total_meanness = np.sum(meanness_ratios)
        print(f"meanness heatmap for 3bv:{testField} (total:{total_meanness})")
        meannesses[testField] = total_meanness
        thing, board = get_render_context(entries, testField)
        minesweeperModel.renderShadedField(thing, board, meanness_ratios)
        print()

    plt.figure(figsize=(10, 6))
    plt.bar(list(range(41)), meannesses, label="stuff", edgecolor="black")
    plt.xlabel("Field (3bv)")
    plt.ylabel("meanness")
    plt.title("Distribution of meanness per field (3bv)")
    unique_fields = [int(x) for x in seed_3bv_lookup.values()]
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.tight_layout()
    plt.legend()
    plt.show(block=True)

def pathway():
    pass

if __name__ == "__main__": # running as main will run random testing/debug stuff
    testFields = list(seed_3bv_lookup.values())
    operation = "averageDifficulty"
    for arg in sys.argv[1:]:
        if arg.isdecimal(): testFields = [int(arg)]
        else: operation = arg

    operations = [cell_reward, averageDifficulty, meanness]
    for op in operations:
        if op.__name__.startswith(operation):
            op(testFields)
            break

