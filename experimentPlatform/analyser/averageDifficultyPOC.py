import numpy as np
from scipy.signal import convolve2d

import json
import datetime
import os
import sys

import minesweeperModel
import solverAlgs
import inputHandler

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

def _move_difficulty_at_xy(domainsArr, xy):
    """
    Your snippet rule:
        for i, domain in enumerate(domainsArr):
            if domain[(x, y)] == domainsArr[-1][(x, y)]:
                return i
    """
    x, y = xy
    if domainsArr is None or len(domainsArr) == 0: return None

    final_domains = domainsArr[-1]
    if final_domains is None or (x, y) not in final_domains: return None

    target = final_domains[(x, y)]
    for i, domain in enumerate(domainsArr):
        if domain is None or (x, y) not in domain:
            continue
        if domain[(x, y)] == target:
            return i
    return None

def do_difficulty_stuff(threebv, entries, render=False, debug=False):
    testField = threebv

    succEntry = None

    fullBoard = inputHandler.board_generate(9, 9, 10, reverse_seed_3bv_lookup[testField])
    height = len(fullBoard)
    width = len(fullBoard[0])

    board_aggregator = np.array([[np.nan if fullBoard[y][x] == -1 else 0 for x in range(width)] for y in range(height)])
    # board_aggregator = [[-1 if fullBoard[y][x] == -1 else 0 for x in range(width)] for y in range(height)]
    fullBoard [fullBoard == -1] = 9 # mask over the mines so they're hidden

    debug = debug or len(entries) < 3

    entry_count = 0
    for entry in entries:
        if seed_3bv_lookup[entry["seed"]] != testField: continue
        if not entry["successful"]: continue
        entry_count += 1

    for entry in entries:
        if seed_3bv_lookup[entry["seed"]] != testField: continue
        if not entry["successful"]: continue

        if succEntry is None: succEntry = entry

        action_analyses = inputHandler.load_preprocessed(entry)

        if (action_analyses is None):
            print("FAIL")
            exit()

        for i in range(1, len(action_analyses)):
            current_boards = action_analyses[i]
            last_boards = action_analyses[i-1]

            moves_made = 0
            for y in range(9):
                for x in range(9):
                    if current_boards[0][(x, y)] != last_boards[0][(x, y)]: # if the cell was opened..
                        moves_made += 1

            local_difficulty = np.zeros(np.shape(board_aggregator))
            for y in range(9):
                for x in range(9):
                    if current_boards[0][(x, y)] != last_boards[0][(x, y)]: # if the cell was opened..
                        local_difficulty[y][x] = _move_difficulty_at_xy(last_boards, (x, y))
            board_aggregator += local_difficulty / entry_count
                
            if not debug: continue

            print(f"loc difficulty for {entry['userIDpriv']}, {entry["timestamp"]}, {entry["seed"]} is")
            hints = inputHandler.resimulate_partial_submission(entry, i, doPrint=False)
            minesweeperModel.phaseRenderDomains(current_boards, hints)
            minesweeperModel.renderShadedField(inputHandler.load_preprocessed(succEntry)[-1], hints, local_difficulty)
            print(local_difficulty)
            for row in local_difficulty:
                if True in (row < 0): exit()

    # print(f"b4 {board_aggregator=}")
    board_aggregator[np.isnan(board_aggregator)] = 0
    # print(f"mid {board_aggregator=}")
    board_aggregator = board_aggregator / np.max(board_aggregator)
    # print(f"aft {board_aggregator=}")

    if render: minesweeperModel.renderShadedField(inputHandler.load_preprocessed(succEntry)[-1], fullBoard, board_aggregator)

    return board_aggregator

if __name__ == "__main__": # running as main will run random testing/debug stuff
    entries = inputHandler.get_all_database_content()

    testEntry = inputHandler.get_database_entry("7478532506737.593", "1770053639277", "1769089890391")
    # testEntry = inputHandler.get_database_entry("9051914951248.672", "1770392320640", "1769089890391")
    # entries = [testEntry]


    if len(sys.argv) > 1: testFields = [int(sys.argv[1])]
    else: testFields = list(seed_3bv_lookup.values())

    difficulties = [0] * 41
    for testField in testFields:
        print(f"typical difficulties for 3bv:{testField}")
        difficulty_data = do_difficulty_stuff(testField, entries, render=True, debug=False)
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
