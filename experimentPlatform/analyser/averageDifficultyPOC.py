import numpy as np
from scipy.signal import convolve2d

import json
import datetime
import os
import sys

import minesweeperModel
import solverAlgs
import inputHandler
import inputHelper

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

def compute_cell_difficulties(threebv, entries, render=False, debug=False):
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
                        local_difficulty[y][x] = inputHelper._move_difficulty_at_xy(last_boards, (x, y))
            board_aggregator += local_difficulty / entry_count
                
            if not debug: continue

            print(f"loc difficulty for {entry['userIDpriv']}, {entry["timestamp"]}, {entry["seed"]} is")
            hints = inputHandler.resimulate_partial_submission(entry, i, doPrint=False)
            minesweeperModel.phaseRenderDomains(current_boards, hints)
            minesweeperModel.renderShadedField(inputHandler.load_preprocessed(succEntry)[-1], hints, local_difficulty)

    board_aggregator[np.isnan(board_aggregator)] = 0
    board_aggregator = board_aggregator / np.max(board_aggregator)

    if render: minesweeperModel.renderShadedField(inputHandler.load_preprocessed(succEntry)[-1], fullBoard, board_aggregator)

    return board_aggregator
