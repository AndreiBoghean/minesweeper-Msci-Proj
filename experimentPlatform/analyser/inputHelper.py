import inputHandler
import minesweeperModel
import solverAlgs

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------- Config / lookups ----------------------------

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

preprocesses = {}
for entry in inputHandler.get_all_database_content():
    action_analyses = inputHandler.load_preprocessed(entry)
    if action_analyses is None:
        print(f"ERROR: {entry=} isnt preprocessed")
        exit()
    preprocesses[entry["_id"]["$oid"]] = action_analyses

raw_database_entries = inputHandler.get_all_database_content(merge_known_identities=True)
manual_outliers = [ inputHandler.get_database_entry("9051914951248.672", "1770650611889", "1769089890388") ]
database_entries = list(filter(lambda entry: [] == [e for e in manual_outliers if e == entry], raw_database_entries))
database_entries_successful = list(filter(lambda entry: entry["successful"], database_entries))

# Build userIDpriv → userIDpub mapping once (keep "last public username wins" behavior)
all_users = list(set([entry["userIDpriv"] for entry in database_entries]))
userPRIV_to_pub = {}
for neededID in all_users[::-1]:
    userPRIV_to_pub[neededID] = f"undef:{neededID}"
    for entry in database_entries:
        if entry["userIDpriv"] == neededID:
            userPRIV_to_pub[neededID] = entry["userIDpub"]
            # break  # actually.. dont break, so that the last public username is used instead of the first one found.

# ---------------------------- Small helpers ----------------------------

_hints_cache = {}
def get_hints(entry):
    seed = entry.get("seed")
    if seed not in _hints_cache:
        board = inputHandler.board_generate(9, 9, 10, seed)
        h = np.copy(board)
        h[h == -1] = 9
        _hints_cache[seed] = h
    return _hints_cache[seed]

def _seed_to_3bv(seed):
    return seed_3bv_lookup.get(str(seed), None)

def _seed_label(seed):
    threebv = _seed_to_3bv(seed)
    return f"field {threebv} (seed {seed})" if threebv is not None else f"seed {seed}"

def _user_label(user_priv):
    return userPRIV_to_pub.get(user_priv, f"undef:{user_priv}")

def _user_pub_to_priv(user_pub):
    return [k for k, v in userPRIV_to_pub.items() if v == user_pub][0]

def _sorted_actions(entry):
    actions = entry.get("actionRecords", [])
    if actions is None:
        return []
    return sorted(actions, key=lambda r: int(r.get("timestamp", 0)))

def _euclid(a, b):
    dx = float(a[0]) - float(b[0])
    dy = float(a[1]) - float(b[1])
    return float(np.sqrt(dx * dx + dy * dy))

def _manhattan(a, b):
    return float(abs(float(a[0]) - float(b[0])) + abs(float(a[1]) - float(b[1])))

def _move_difficulty_at_xy(domainsArr, xy):
    """
    Your snippet rule:
        for i, domain in enumerate(domainsArr):
            if domain[(x, y)] == domainsArr[-1][(x, y)]:
                return i
    """
    x, y = xy
    if domainsArr is None or len(domainsArr) == 0:
        return None
    final_domains = domainsArr[-1]
    if final_domains is None or (x, y) not in final_domains:
        return None
    target = final_domains[(x, y)]
    for i, domain in enumerate(domainsArr):
        if domain is None or (x, y) not in domain:
            continue
        if domain[(x, y)] == target:
            return i
    return None
