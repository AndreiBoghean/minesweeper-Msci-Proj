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

testEntry = inputHandler.get_database_entry("7478532506737.593", "1770053639277", "1769089890391")

if __name__ == "__main__": # running as main will run random testing/debug stuff
    testField = 13
    if len(sys.argv) > 1: testField = int(sys.argv[1])
    copiable_board = [[-1 for x in range(9)] for y in range(9)]

    for entry in inputHandler.get_all_database_content():

        # entry = testEntry
        if seed_3bv_lookup[entry["seed"]] != testField: continue
        if not entry["successful"]: continue

        print(entry["userIDpub"])

        action_analyses = inputHandler.load_preprocessed(entry)

        if (action_analyses is None):
            print("FAIL")
            exit()

        cell_open_timestamps = np.array(copiable_board)

        for i in range(len(action_analyses)):
            current_board = action_analyses[i][0]

            for y in range(9):
                for x in range(9):

                    if current_board[(x, y)] == [True, False]: # if the cell is open
                        if cell_open_timestamps[y][x] == -1:
                            cell_open_timestamps[y][x] = i

        # print(cell_open_timestamps)
        # print(np.max(cell_open_timestamps))
        cell_open_timestamps = cell_open_timestamps / np.max(cell_open_timestamps)
        # hints = inputHandler.resimulate_partial_submission(entry, -1, doPrint = False)
        hints = inputHandler.board_generate(9, 9, 10, entry["seed"])
        hints[hints == -1] = 9
        # minesweeperModel.phaseRenderDomains(action_analyses[-1], hints)
        minesweeperModel.renderShadedField(action_analyses[-1], hints, cell_open_timestamps)

        print()
