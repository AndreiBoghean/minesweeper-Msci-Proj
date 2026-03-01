import numpy as np
from scipy.signal import convolve2d

import json
import datetime
import os
import sys

import minesweeperModel
import solverAlgs
import inputHandler

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

def find_possible_moves(domainsArr, hints):
    width = len(hints[0])
    height = len(hints)

    possible_moves_count = 0
    for y in range(height):
        for x in range(width):
            move_possible = 0
            for i, domain in enumerate(domainsArr):
                if domain[(x, y)] == domainsArr[-1][(x, y)]:
                    move_possible = i
                    break

            if move_possible != 0:
                possible_moves_count += 1

    return possible_moves_count

# testEntry = inputHandler.get_database_entry("7478532506737.593", "1770053639277", "1769089890391")
succEntry = None

if __name__ == "__main__": # running as main will run random testing/debug stuff
    testField = 13
    if len(sys.argv) > 1: testField = int(sys.argv[1])
    board_aggregator = [[-1 for x in range(9)] for y in range(9)]

    # hints = inputHandler.resimulate_partial_submission(testEntry, -1, doPrint = False)
    hints = inputHandler.board_generate(9, 9, 10, reverse_seed_3bv_lookup[testField])
    hints[hints == -1] = 9

    for entry in inputHandler.get_all_database_content():

        # entry = testEntry
        if seed_3bv_lookup[entry["seed"]] != testField: continue
        if not entry["successful"]: continue

        if succEntry is None:
            succEntry = entry

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

            for y in range(9):
                for x in range(9):
                    if current_boards[0][(x, y)] != last_boards[0][(x, y)]: # if the cell was opened..
                        board_aggregator[y][x] += find_possible_moves(current_boards, hints) - find_possible_moves(last_boards, hints) + moves_made

    board_aggregator = board_aggregator / np.max(board_aggregator)
    minesweeperModel.renderShadedField(inputHandler.load_preprocessed(succEntry)[-1], hints, board_aggregator)

    print()
