import numpy as np
from scipy.signal import convolve2d

import json
import datetime
import os
import sys

import minesweeperModel
import solverAlgs

testCaseMines3 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
])


testCase4 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 9, 1, 0, 0, 0],
    [0, 0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
])

testCase5 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 9, 1, 0, 0, 0],
    [0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
])

testCase6 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 9, 1, 0, 0, 0],
    [0, 0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 9, 9, 9, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
])

testCasePAPERv1 = np.array([
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 0],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2, 1, 1, 1, 0],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 0],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1, 0, 1, 1],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2, 1, 2, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 2, 1, 2, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 1, 1, 1, 1, 0, 2, 9, 4, 2, 1],
    [9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
    [9, 9, 2, 2, 3, 2, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [9, 9, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 9, 1, 0],
    [9, 9, 3, 3, 3, 2, 1, 1, 9, 1, 0, 0, 1, 1, 1, 0],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 0, 0, 0]
])

testCasePAPERv1small = np.array([
    [9, 9, 9, 9, 9, 1, 0],
    [9, 9, 2, 1, 1, 1, 0],
    [9, 9, 1, 0, 0, 0, 0],
    [9, 9, 1, 1, 0, 1, 1],
    [9, 9, 9, 2, 1, 2, 9],
    [9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9],
])

testCasePAPERv2 = np.array([
    [0, 0, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1],
    [0, 0, 1, 1, 2, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [0, 0, 2, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [0, 0, 2, 9, 9, 9, 9, 9, 9, 9, 2, 1, 3, 9, 9, 9],
    [0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 2, 0, 1, 9, 9, 9],
    [1, 1, 1, 9, 9, 9, 9, 9, 9, 9, 2, 0, 1, 1, 2, 1],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2, 0, 0, 0, 0, 0],
    [9, 2, 2, 1, 2, 3, 9, 2, 2, 1, 1, 1, 1, 1, 0, 0],
    [9, 9, 2, 0, 0, 1, 9, 1, 0, 0, 0, 1, 9, 1, 0, 0],
    [9, 9, 3, 1, 1, 1, 9, 1, 0, 0, 0, 2, 9, 2, 0, 0],
    [9, 9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 1, 9, 2, 1, 0],
    [9, 9, 9, 9, 9, 9, 9, 2, 1, 0, 0, 1, 2, 9, 2, 1],
    [9, 9, 9, 9, 9, 9, 9, 9, 2, 1, 0, 0, 2, 9, 9, 9],
    [9, 9, 9, 9, 9, 3, 1, 2, 9, 1, 0, 1, 3, 9, 3, 1],
    [9, 9, 9, 9, 9, 3, 0, 1, 1, 1, 0, 1, 9, 9, 2, 0],
    [9, 9, 9, 9, 9, 2, 0, 0, 0, 0, 0, 1, 9, 9, 1, 0]
])

testCasePAPERv3 = np.array([
    [0, 0, 0, 0, 0, 0, 0, 1, 9],
    [0, 0, 0, 0, 0, 0, 0, 2, 9],
    [0, 0, 0, 0, 0, 0, 0, 1, 9],
    [0, 0, 0, 0, 0, 0, 0, 2, 9],
    [0, 0, 0, 0, 0, 0, 0, 1, 9],
    [0, 0, 0, 0, 0, 0, 0, 2, 9],
    [0, 0, 0, 0, 0, 0, 0, 1, 9],
    [0, 0, 0, 0, 0, 0, 0, 2, 9],
    [0, 0, 0, 0, 0, 0, 0, 1, 9],
])

testCaseFullySolvedV1 = np.array([
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 9, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 9, 1],
    [1, 9, 1, 0, 0, 1, 2, 3, 2],
    [1, 1, 1, 0, 1, 2, 9, 4, 9],
    [0, 0, 0, 0, 2, 9, 4, 9, 9],
    [0, 0, 0, 0, 2, 9, 3, 2, 2],
    [0, 0, 1, 1, 2, 1, 1, 0, 0],
    [0, 0, 1, 9, 1, 0, 0, 0, 0],
])

def get_test_input():

    chosenTestCase = testCase5

    testCaseMines = np.copy(chosenTestCase)
    testCaseMines[chosenTestCase != 1] = 0

    testCaseHidden = np.copy(chosenTestCase)
    testCaseHidden[testCaseHidden != 9] = 0


    # choose mine arrangement.. # grid of 0s and 1s for safe, not safe
    mines = testCaseMines

    # create hints.. 0-8
    kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    hints = convolve2d(mines, kernel, "same")

    # choose hiddens arrangement.. grid of 0s and 1s for revealed, hidden
    hiddens = testCaseHidden

    # build final input.. 0-8 for hint, 9 for hidden. # HACK: using 9 to represent covered cells in the hints representation.
    input = hints # start from the hints
    input[mines==1] = 9 # remove the hints that are actually mines
    input[hiddens!=0] = 9 # remove the hints that are not visible.


    ################# PARTIAL CONTROL INPUT PARSING

    # return testCaseFullySolvedV1
    return testCasePAPERv1


# database things we need:
# 1. get all attempts
# 2. get one specific attempt by some ID (presumably by the same ID the website and database uses)
# 3. get a random attempt (maybe?.. just for fun.. probs wont use.)

# consideration: will we ever connect directly to the database to get things?
# probably not.. there's no need for experimentation. we just need a local dataset to test-run statistics,
# and when we do the big "final" statitsics run, we will just download the whole dataset manually.

def get_all_database_content():
    with open("testData/testData.json") as f:
        jayson = json.load(f)
        return jayson

def get_database_entry(userIDpriv, timestamp, seed): # note: IDpriv, timestamp, seed makes up our internal primary key for user submissions.
    database_data = get_all_database_content()

    for submission in database_data:
        if submission["userIDpriv"] == userIDpriv and submission["timestamp"] == timestamp and submission["seed"] == seed:
            return submission

def mine_generate(fieldWidth, fieldHeight, mineCount, seed):
    with open("seedRenders.json") as f:
        jayson = json.load(f)
        return np.array(jayson[str(seed)])

# gave up on directly recreating mines.. I'm making a node.js script instead because js does floats and float bitwise operations wierdly and jumping to javascript and importing it into python is easier
# def mine_generate(fieldWidth, fieldHeight, mineCount, seed):
#     # NOTE: see how the javascript variant does it as reference for python implementation
#     """
#     let seedIter = mineSeed
# 
#     let game = []
#     for (let _ = 0; _ < fieldHeight; _++) game.push(Array(fieldWidth).fill(0));
# 
#     for (let _ = 0; _ < mineCount; _++) {
#         const randProb = (seedIter = seedIter * 16807 % 2147483647) / 2147483646;
#         const mineIndex = Math.round((fieldWidth*fieldHeight-1) * randProb)
#         const y = mineIndex % fieldWidth, x = Math.round(mineIndex / fieldHeight)
#         // console.log("indexes:", x, y);
#         if (game[y][x] == 0) game[y][x] = 1;
#         else _ -= 1
#     }30-3
# 
#     return [game, mineSeed];
#     """
#     
#     seedIter = seed
#     game = np.zeros((fieldHeight, fieldWidth))
# 
#     mN = 0 # mN is number of mines placed so far
#     while mN < mineCount:
#         seedIter = (seedIter * 16807) & 2147483647.0
# 
#         randProb = seedIter / 2147483646
#         mineIndex = round((fieldWidth*fieldHeight-1) * randProb)
# 
#         print("on randProb", randProb)
#         y = mineIndex % fieldWidth
#         x  = mineIndex // fieldHeight
# 
#         if game[y, x] == 0:
#             game[y, x] = 1
#             mN += 1
# 
#     return game

def board_generate(fieldWidth, fieldHeight, mineCount, seed):
    minesLayout = mine_generate(fieldWidth, fieldHeight, mineCount, seed)

    kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    hints = convolve2d(minesLayout, kernel, "same")

    hints[minesLayout==1] = -1 # mask minesLayout ontop of the hints using 9 as the mine indicator
    return hints
    # return testCasePAPERv1

def reveal_cell(progressing_board, uncovered_board, cellX, cellY):
    # print("revealing", cellX, cellY)

    progressing_board[cellY, cellX] = uncovered_board[cellY, cellX]
    if progressing_board[cellY, cellX] == 0:
        zero_propogate(progressing_board, uncovered_board, cellX, cellY)

def zero_propogate(progressing_board, uncovered_board, cellX, cellY):
    for neighY in range(cellY-1, cellY+2):
        for neighX in range(cellX-1, cellX+2):
            if (neighX != cellX or neighY != cellY) and neighX >= 0 and neighX < uncovered_board.shape[1] and neighY >= 0 and neighY < uncovered_board.shape[0]:
                if progressing_board[neighY, neighX] == 9: # if is hidden..
                    reveal_cell(progressing_board, uncovered_board, neighX, neighY)

def chord(progressing_board, uncovered_board, cellX, cellY):
    # HACK: the frontend validates chords so they can only be attempted if count(neighbourFlags)==hint. this means we can assume each chord either has the exact correct flags, or doesnt (if we didnt have client-side validation, then the user could trigger a chord with more flags than empty spaces, which would give us ambiguity and would make validating this much more annoying right now.
    for neighY in range(cellY-1, cellY+2):
        for neighX in range(cellX-1, cellX+2):
            if (neighX != cellX or neighY != cellY) and neighX >= 0 and neighX < uncovered_board.shape[1] and neighY >= 0 and neighY < uncovered_board.shape[0]:
                if uncovered_board[neighY, neighX] != -1: # if not a mine.. (also.. see above HACK)
                    reveal_cell(progressing_board, uncovered_board, neighX, neighY)

# steps=0 returns the unattempted board. steps=1 will have one step applied, etc.
# note that we want this to give us in a form that solverAlgs likes. that is - 0-9 for hints and 9 for a hidden cell.
# problem: what happens when a mine appears? I'm going to need to represent it..
# for now.. I'll just make it -1 , and hope it shouldnt ever be a problem because solverAlgs shouldnt ever get run on a field with a mine, because at that point the game is over and there is no subsequent move.
def resimulate_partial_submission(submission, steps, doPrint = True):
    if not doPrint:
        # print_storage = print
        print = lambda *args, **kwargs: None

    # note.. what am I going to make this method do? it will contain just hints and mines.
    # that will be 0-9 for hints, and probablly also -1 for mines.
    uncovered_board = board_generate(9, 9, 10, submission["seed"]) # assumed 9x9 field with 10 mines; HACK: submission seed should be float if we were doing a real RNG, but because of javascript flaot wierdness we're using a string
    progressing_board = np.full(uncovered_board.shape, 9)

    i = 0
    for action in submission["actionRecords"]:
        if i == steps: return progressing_board
        if not action["successful"]:
            print("unsuccessful")
            continue
        i+= 1

        actionX, actionY = action["x"], action["y"]

        # print("progressing_board:")
        # print(progressing_board)

        match action["actionID"]:
            case 0: # left click (pimary action) / opens a cell.
                print("left click", actionX, actionY)
                progressing_board[actionY, actionX] = uncovered_board[actionY, actionX] # copy the hint from the source of truth into the current board state.
                reveal_cell(progressing_board, uncovered_board, actionX, actionY)
            case 1: # right click (secondary action) / either toggles flag or triggers a chord
                # if flag action then ignore.. otherwise trigger chord. remember actions are guaranteed successfull. if the cell was opened, then it's certainly a chord action.
                if progressing_board[actionY, actionX] != 9:
                    print("rc chord", actionX, actionY)
                    chord(progressing_board, uncovered_board, actionX, actionY)
                else:
                    print("flag", actionX, actionY)
                    i -= 1
            case 2: # dedicated chord action via left+right click
                print("chord init", actionX, actionY)
                chord(progressing_board, uncovered_board, actionX, actionY)
            case 3: # actionID 3 is restart button clicked down
                print("reset start")
                i -= 1
                break # game is over.. nothing else for us to do..
            case 4: # actionID 4 is restart button click released
                print("reset done")
                i -= 1
                break # game is over.. nothing else for us to do..

    if i == steps or steps == -1: return progressing_board
    return None


def entry_to_filename(entry):
    pid = entry["userIDpriv"]
    seed = entry["seed"]
    timestamp = entry["timestamp"]
    return f"testData/dataPreprocesses/{seed}_{timestamp}_{pid}.json"

def store_preprocess(entry, action_analyses, overwrite=False):
    filename = entry_to_filename(entry)
    if os.path.exists(filename) and not overwrite:
        print(f"file {filename} already present.. skipping")
        return

    # remove tuples since json doesnt like them
    # WARN: assumes 9x9 minesweeper field.

    action_analyses = [[{(key[0]+key[1]*9):val  for key, val in phase.items()} for phase in actionStep] for actionStep in action_analyses]

    json_str = json.dumps(action_analyses, indent=4)
    print(f"{filename=}")
    with open(filename, "w") as f:
        f.write(json_str)

def load_preprocessed(entry):
    filename = entry_to_filename(entry)
    if not os.path.exists(filename):
        print(f"file {filename} doesnt exist..")
        return None

    with open(filename) as f:
        data = json.load(f)

        # for actionStep in data:
        #     for phase in actionStep:
        #         print(phase)

        return [[{(int(key)%9, int(key)//9):val  for key, val in phase.items()} for phase in actionStep] for actionStep in data]


def process_entry(entry, doPrint=False):
    if not doPrint:
        print_storage = print
        # print = lambda *args, **kwargs: None

    action_analyses = []
    start_time = datetime.datetime.now()
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    for i in range(len(entry["actionRecords"])+1): # i is an index, but resimulate takes a count
        print(f"the game after {i} moves:")

        current_board = resimulate_partial_submission(entry, i)
        if current_board is None:
            print("reached end of gameplay")
            break

        domains = minesweeperModel.create_domains(current_board)
        constraints = minesweeperModel.build_constraints(current_board, domains)

        domainsArr = [domains]
        for i in range(3):
            domains = domainsArr[0]
            constraints = minesweeperModel.build_constraints(current_board, domains)

            if i == 0: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=1)
            elif i == 1: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=2)
            elif i == 2: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=1, rac_m=3)
            else: domains = solverAlgs.relationalArcConsistency(domains, constraints, rac_i=2, rac_m=3)

            domainsArr.append(domains)

        action_analyses.append(domainsArr)
        minesweeperModel.phaseRenderDomains(domainsArr, current_board)
        print(f"at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (started {start_time_str}) (taking {round((datetime.datetime.now()-start_time).seconds//60, 3)}m {(datetime.datetime.now()-start_time).seconds % 60}s)", end="\r")
        print()

    return action_analyses




def preprocess_all_entries(threadCount=1, threadID=0):
    for i, entry in enumerate(get_all_database_content()):
        if i%threadCount != threadID:
            continue

        action_analyses = load_preprocessed(entry)
        if (action_analyses is None): action_analyses = process_entry(entry)

        for i, domainsArr in enumerate(action_analyses):
            current_board = resimulate_partial_submission(entry, i)
            print(f"the game after {i} moves:")
            minesweeperModel.phaseRenderDomains(domainsArr, current_board)


        store_preprocess(entry, action_analyses)


if __name__ == "__main__": # running as main will run random testing/debug stuff

    # assumes the first arg is thread count, and 2nd arg is our thread ID.
    # multi-processing is done manually by openning many terminal windows and running this script in each window with a new ID given to each instance.
    # note that we all read the same userData.json, so it's technically possible two of us will try to read it at the same time when we're initially spinning up, but that is highly unlikely.
    preprocess_all_entries(int(sys.argv[1]), int(sys.argv[2]))
    exit()

    testEntry = get_database_entry("7478532506737.593", "1770053639277", "1769089890391")

    action_analyses = load_preprocessed(testEntry)
    if (action_analyses is None): action_analyses = process_entry(testEntry)

    for i, domainsArr in enumerate(action_analyses):
        current_board = resimulate_partial_submission(testEntry, i)
        print(f"the game after {i} moves:")
        minesweeperModel.phaseRenderDomains(domainsArr, current_board)


    store_preprocess(testEntry, action_analyses)
