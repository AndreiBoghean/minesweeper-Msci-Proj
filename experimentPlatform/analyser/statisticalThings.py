import inputHandler
import minesweeperModel
import solverAlgs

import matplotlib.pyplot as plt
import numpy as np

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

reverse_seed_3bv_lookup = { threebv: seed for seed, threebv in seed_3bv_lookup.items() }

database_entries = inputHandler.get_all_database_content()
database_entries_successful = list(filter(lambda entry: entry["successful"], inputHandler.get_all_database_content()))


# Build userIDpriv → userIDpub mapping once
all_users = list(set([entry["userIDpriv"] for entry in database_entries]))
userPRIV_to_pub = {}
for neededID in all_users[::-1]:
    userPRIV_to_pub[neededID] = f"undef:{neededID}"
    for entry in database_entries:
        if entry["userIDpriv"] == neededID:
            userPRIV_to_pub[neededID] = entry["userIDpub"]
            # break # actually.. dont break, so that the last public username is used instead of the first one found.

######################################################### STUFF NOT USING CONSTRAINT SOLVER.. JUST SURFACE LEVEL STATISTICS

"""
things we will be wanting to do here:

make a distribution of submissions w.r.t. people -- ALSO: break the bar into successful,unsuccessful.
distribution of average solve times w.r.t. different FIELDS (now shown as 3bv)
distribution of average solve times w.r.t. different FIELDS for SPECIFIC PEOPLE (3bv on x)
NEW: distribution of submissions per field seed (3bv on x)

also need some stuff to look at learning effects...
plot of solve times as attempt counts increase, with multiple plots for multiple people, for A SPECIFIC FIELD (seed → 3bv in title)

^ learning effects problem: learning effects aggregate within a "session", and then across different days people may partially forget their leraning effects?

"""



# THING 1.
def plot_submissions_per_person(database_entries, database_entries_successful):
    """
    Bar chart: number of submissions per person (userIDpub on plot, userIDpriv internally).
    """
    plt.figure(figsize=(10, 6))

    user_ids = [entry["userIDpriv"] for entry in database_entries]
    unique_users, counts = np.unique(user_ids, return_counts=True)
    labels = [userPRIV_to_pub[u] for u in unique_users]
    plt.bar(labels, counts, color="red", edgecolor="black")

    user_ids = [entry["userIDpriv"] for entry in database_entries_successful]
    unique_users, counts = np.unique(user_ids, return_counts=True)
    labels = [userPRIV_to_pub[u] for u in unique_users]
    plt.bar(labels, counts, color="green", edgecolor="black")

    plt.xlabel("User")
    plt.ylabel("Number of submissions")
    plt.title("Distribution of submissions per person")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)


def plot_submissions_per_userAGENT(database_entries):
    """
    Bar chart: number of submissions per userAgent.
    """
    user_agents = [entry["userAgent"] for entry in database_entries]
    unique_agents, counts = np.unique(user_agents, return_counts=True)

    plt.figure(figsize=(10, 6))
    plt.bar(unique_agents, counts, color="skyblue", edgecolor="black")
    plt.xlabel("UserAgent")
    plt.ylabel("Number of submissions")
    plt.title("Distribution of submissions per userAgent")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show(block=False)


def plot_submissions_per_field_3bv(database_entries, database_entries_successful):
    """
    Bar chart: number of submissions per field (x axis = 3bv, via seed_3bv_lookup).
    """
    plt.figure(figsize=(10, 6))

    fields = []
    for entry in database_entries:
        seed = entry.get("seed")
        if seed is None:
            continue
        try:
            threebv = seed_3bv_lookup[seed]
            fields.append(threebv)
        except KeyError:
            continue

    if not fields:
        print("No valid fields (3bv) found for submissions per field.")
        return

    unique_fields, counts = np.unique(fields, return_counts=True)
    plt.bar(unique_fields, counts, label="all submissions", color="red", edgecolor="black")

    fields = []
    for entry in database_entries_successful:
        seed = entry.get("seed")
        if seed is None:
            continue
        try:
            threebv = seed_3bv_lookup[seed]
            fields.append(threebv)
        except KeyError:
            continue

    if not fields:
        print("No valid fields (3bv) found for submissions per field.")
        return

    unique_fields, counts = np.unique(fields, return_counts=True)
    plt.bar(unique_fields, counts, label="successful only", color="green", edgecolor="black")



    plt.xlabel("Field (3bv)")
    plt.ylabel("Number of submissions")
    plt.title("Distribution of submissions per field (3bv)")
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)




# THING 2.
def plot_min_solve_time_per_field(database_entries):
    """
    Bar chart: average solve time (duration) per field (x axis = 3bv, via seed_3bv_lookup).
    Only successful runs are considered.
    """
    durations = []
    fields = []

    for entry in database_entries:
        try:
            dur = float(entry["duration"]) / 1000
            seed = entry["seed"]
            threebv = seed_3bv_lookup[seed]
            if dur < 0.05: continue
            if len(entry["actionRecords"]) < threebv: continue
            durations.append(dur)
            fields.append(threebv)
        except (KeyError, ValueError, KeyError):
            continue

    if not durations:
        print("No valid durations found.")
        return

    durations = np.array(durations)
    fields = np.array(fields)

    unique_fields, idx = np.unique(fields, return_inverse=True)
    avg_times = [durations[idx == i].min() for i in range(len(unique_fields))]

    plt.figure(figsize=(10, 6))
    plt.grid(axis="y")
    plt.bar(unique_fields, avg_times, color="lightcoral", edgecolor="black")
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.yticks(ticks=np.arange(0, 85, step=2.5))
    plt.xlabel("Field (3bv)")
    plt.ylabel("Min solve time (s)")
    plt.title("Min solve time per field (3bv)")
    plt.tight_layout()
    plt.show(block=False)

def plot_avg_solve_time_per_field(database_entries):
    """
    Bar chart: average solve time (duration) per field (x axis = 3bv, via seed_3bv_lookup).
    Only successful runs are considered.
    """
    durations = []
    fields = []

    for entry in database_entries:
        try:
            dur = float(entry["duration"]) / 1000
            seed = entry["seed"]
            threebv = seed_3bv_lookup[seed]
            durations.append(dur)
            fields.append(threebv)
        except (KeyError, ValueError, KeyError):
            continue

    if not durations:
        print("No valid durations found.")
        return

    durations = np.array(durations)
    fields = np.array(fields)

    unique_fields, idx = np.unique(fields, return_inverse=True)
    avg_times = [durations[idx == i].mean() for i in range(len(unique_fields))]

    plt.figure(figsize=(10, 6))
    plt.grid(axis="y")
    plt.bar(unique_fields, avg_times, color="lightcoral", edgecolor="black")
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.yticks(ticks=np.arange(0, 85, step=2.5))
    plt.xlabel("Field (3bv)")
    plt.ylabel("Average solve time (s)")
    plt.title("Average solve time per field (3bv)")
    plt.tight_layout()
    plt.show(block=False)


# THING 3.
def plot_avg_solve_time_per_field_per_person(database_entries, target_users, userPRIV_to_pub):
    """
    Bar chart for each target user: average solve time per field (x axis = 3bv).
    Uses userIDpriv internally, userIDpub for plot label.
    """
    for user in target_users:
        durations = []
        fields = []

        for entry in database_entries:
            if entry["userIDpriv"] != user:
                continue
            try:
                dur = float(entry["duration"]) / 1000
                seed = entry["seed"]
                threebv = seed_3bv_lookup[seed]
                durations.append(dur)
                fields.append(threebv)
            except (KeyError, ValueError, KeyError):
                continue

        if not durations:
            print(f"No data for user {user}.")
            continue

        durations = np.array(durations)
        fields = np.array(fields)

        unique_fields, idx = np.unique(fields, return_inverse=True)
        avg_times = [durations[idx == i].mean() for i in range(len(unique_fields))]

        plt.figure(figsize=(8, 5))
        plt.bar(unique_fields, avg_times, color="mediumpurple", edgecolor="black")
        plt.xticks(ticks=unique_fields, labels=unique_fields)
        plt.xlabel("Field (3bv)")
        plt.ylabel("Average solve time (s)")
        plt.title(f"Average solve time per field – {userPRIV_to_pub[user]}")
        plt.tight_layout()
        plt.show(block=False)


# THING 4.
def plot_learning_curve_per_person_per_field(database_entries, target_users, field_value, userPRIV_to_pub, min_attempts=3):
    """
    For each target user, plot solve time vs attempt number (within a specific field),
    showing learning effects over attempts.
    Uses userIDpriv internally, userIDpub for legend label.
    Field value is seed; title shows corresponding 3bv.
    """
    seed = field_value
    try:
        threebv = seed_3bv_lookup[seed]
    except KeyError:
        print(f"Seed {seed} not in seed_3bv_lookup.")
        return

    plt.figure(figsize=(8, 5))

    for user in target_users:
        entries = [
            e
            for e in database_entries
            if e["userIDpriv"] == user
            and str(e.get("seed", "")) == str(seed)
        ]

        if len(entries) < min_attempts:
            print(f"Skipping {user}: only {len(entries)} attempts for field {seed}.")
            continue

        # Sort by timestamp
        entries.sort(key=lambda x: int(x["timestamp"]))

        durations = [float(x["duration"]) for x in entries]
        attempts = list(range(1, len(durations) + 1))

        plt.plot(attempts, durations, linestyle="-", label=f"{userPRIV_to_pub[user]}")

    plt.xlabel("Attempt number")
    plt.ylabel("Solve time (ms)")
    plt.title(f"Learning curves of different users for field {threebv} (seed {seed})")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)

# THING 5.
def plot_move_distance_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30, distance_metric="euclidean", color=None):
    """
    Histogram (density=True) of distances between consecutive moves.

    You control the 4 modes via the two optional filters:
      1) only_seed=None,  only_user_priv=None   -> all maps, all people
      2) only_seed=...,   only_user_priv=None   -> one map, all people
      3) only_seed=None,  only_user_priv=...    -> all maps, one person
      4) only_seed=...,   only_user_priv=...    -> one map, one person

    Distance is computed between consecutive actionRecords (sorted by action timestamp)
    using either:
      - distance_metric="euclidean": sqrt(dx^2 + dy^2)
      - distance_metric="manhattan": |dx| + |dy|

    Notes:
    - Uses userIDpriv for filtering, but uses userIDpub in the plot title when possible.
    - Skips submissions with <2 actionRecords.
    """
    def dist(a, b):
        dx = float(a["x"]) - float(b["x"])
        dy = float(a["y"]) - float(b["y"])
        if distance_metric == "euclidean":
            return float(np.sqrt(dx * dx + dy * dy))
        if distance_metric == "manhattan":
            return float(abs(dx) + abs(dy))
        raise ValueError(f"Unknown distance_metric={distance_metric}")

    distances = []

    for entry in database_entries:
        if only_seed is not None and str(entry.get("seed")) != str(only_seed):
            continue
        if only_user_priv is not None and entry.get("userIDpriv") != only_user_priv:
            continue

        records = entry.get("actionRecords", [])
        if records is None or len(records) < 2:
            continue

        # sort within-submission actions by their own timestamp (not submission timestamp)
        records = sorted(records, key=lambda r: int(r.get("timestamp", 0)))

        for i in range(1, len(records)):
            a = records[i - 1]
            b = records[i]
            if "x" not in a or "y" not in a or "x" not in b or "y" not in b:
                continue
            distances.append(dist(a, b))

    if len(distances) == 0:
        print("No distances found for the given filters.")
        return

    distances = np.array(distances, dtype=float)

    # Title pieces (show 3bv when seed is provided and you have the lookup in global scope)
    user_part = "all people"
    if only_user_priv is not None:
        user_part = userPRIV_to_pub.get(only_user_priv, f"undef:{only_user_priv}")

    plt.hist(distances, bins=bins, label=user_part, density=True, color=color, edgecolor="black", alpha=0.85)  # density=True normalizes area to 1 [web:59]

def plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None], bins=30, distance_metric="euclidean"):
    """
    Histogram (density=True) of distances between consecutive moves.

    You control the 4 modes via the two optional filters:
      1) only_seed=None,  only_user_priv=None   -> all maps, all people
      2) only_seed=...,   only_user_priv=None   -> one map, all people
      3) only_seed=None,  only_user_priv=...    -> all maps, one person
      4) only_seed=...,   only_user_priv=...    -> one map, one person

    Distance is computed between consecutive actionRecords (sorted by action timestamp)
    using either:
      - distance_metric="euclidean": sqrt(dx^2 + dy^2)
      - distance_metric="manhattan": |dx| + |dy|

    Notes:
    - Uses userIDpriv for filtering, but uses userIDpub in the plot title when possible.
    - Skips submissions with <2 actionRecords.
    """

    field_part = "all maps"
    if only_seed is not None:
        threebv = seed_3bv_lookup.get(str(only_seed), None)
        field_part = f"field {threebv} (seed {only_seed})" if threebv is not None else f"seed {only_seed}"

    plt.figure(figsize=(9, 5))

    for user in users:
        plot_move_distance_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=user, bins=30, distance_metric="euclidean", color=None)

    plt.xlabel(f"Move distance ({distance_metric})")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of distance between moves ({field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)

def plot_move_time_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30, time_unit="s", include_first_move=False, clip_min=None, clip_max=None, color=None):
    """
    Histogram (density=True) of time-to-make-a-move, computed from actionRecords timestamps.

    4 modes via two optional filters:
      1) only_seed=None,  only_user_priv=None   -> all maps, all people
      2) only_seed=...,   only_user_priv=None   -> one map, all people
      3) only_seed=None,  only_user_priv=...    -> all maps, one person
      4) only_seed=...,   only_user_priv=...    -> one map, one person

    Move time definition:
      dt_i = timestamp(action_i) - timestamp(action_{i-1}) within a single submission,
      with actionRecords sorted by their own timestamp.
    By default, the first action has no dt and is excluded unless include_first_move=True,
    in which case dt_1 is set to 0.

    Parameters:
    - time_unit: "ms" or "s" (your actionRecord timestamps look like ms).
    - clip_min/clip_max: optional numeric clipping after unit conversion (e.g., clip_max=10 for <=10s).
    - Uses userIDpriv for filtering, uses userIDpub for plot labeling.

    Depends on globals in your file:
    - seed_3bv_lookup (for showing 3bv in title when only_seed is set).
    """
    dts = []

    for entry in database_entries:
        if only_seed is not None and str(entry.get("seed")) != str(only_seed):
            continue
        if only_user_priv is not None and entry.get("userIDpriv") != only_user_priv:
            continue

        records = entry.get("actionRecords", [])
        if records is None or len(records) == 0:
            continue

        records = sorted(records, key=lambda r: int(r.get("timestamp", 0)))
        ts = []
        for r in records:
            if "timestamp" not in r:
                continue
            try:
                ts.append(int(r["timestamp"]))
            except ValueError:
                continue

        if len(ts) == 0:
            continue

        if include_first_move:
            dts.append(0)

        if len(ts) >= 2:
            diffs = np.diff(np.array(ts, dtype=np.int64))  # consecutive deltas [web:80]
            dts.extend(diffs.tolist())

    if len(dts) == 0:
        print("No move times found for the given filters.")
        return

    dts = np.array(dts, dtype=float)

    # unit conversion
    if time_unit == "ms":
        pass
    elif time_unit == "s":
        dts = dts / 1000.0
    else:
        raise ValueError("time_unit must be 'ms' or 's'")

    # optional clipping
    if clip_min is not None:
        dts = dts[dts >= float(clip_min)]
    if clip_max is not None:
        dts = dts[dts <= float(clip_max)]

    if len(dts) == 0:
        print("All move times removed by clipping.")
        return

    user_part = "all people"
    if only_user_priv is not None:
        user_part = userPRIV_to_pub.get(only_user_priv, f"undef:{only_user_priv}")

    # plt.hist(dts, label=user_part, bins=bins, density=True, color=color, edgecolor="black", alpha=0.55)  # density=True normalizes area to 1 [web:59]
    plt.hist(dts, label=user_part, bins=bins, density=True, edgecolor="black", alpha=0.55, color=color)  # density=True normalizes area to 1 [web:59]

def plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None], bins=30, time_unit="s", include_first_move=False, clip_min=None, clip_max=None):
    plt.figure(figsize=(9, 5))

    colors = ["navy", "orange", "pink", "brown"]
    for user in users: 
        # plot_move_time_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed, user, bins, time_unit, include_first_move, clip_min, clip_max, color=colors.pop() if user is not None else "seagreen")
        plot_move_time_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed, user, bins, time_unit, include_first_move, clip_min, clip_max)

    field_part = "all maps"
    if only_seed is not None:
        threebv = seed_3bv_lookup.get(str(only_seed), None)
        field_part = f"field {threebv} (seed {only_seed})" if threebv is not None else f"seed {only_seed}"

    plt.xlabel(f"Time between moves ({time_unit})")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of time-to-make-a-move ({field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)

def plot_move_time_histogram(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30, time_unit="s", include_first_move=False, clip_min=None, clip_max=None):
    """
    Histogram (density=True) of time-to-make-a-move, computed from actionRecords timestamps.

    4 modes via two optional filters:
      1) only_seed=None,  only_user_priv=None   -> all maps, all people
      2) only_seed=...,   only_user_priv=None   -> one map, all people
      3) only_seed=None,  only_user_priv=...    -> all maps, one person
      4) only_seed=...,   only_user_priv=...    -> one map, one person

    Move time definition:
      dt_i = timestamp(action_i) - timestamp(action_{i-1}) within a single submission,
      with actionRecords sorted by their own timestamp.
    By default, the first action has no dt and is excluded unless include_first_move=True,
    in which case dt_1 is set to 0.

    Parameters:
    - time_unit: "ms" or "s" (your actionRecord timestamps look like ms).
    - clip_min/clip_max: optional numeric clipping after unit conversion (e.g., clip_max=10 for <=10s).
    - Uses userIDpriv for filtering, uses userIDpub for plot labeling.

    Depends on globals in your file:
    - seed_3bv_lookup (for showing 3bv in title when only_seed is set).
    """
    import matplotlib.pyplot as plt
    import numpy as np

    dts = []

    for entry in database_entries:
        if only_seed is not None and str(entry.get("seed")) != str(only_seed):
            continue
        if only_user_priv is not None and entry.get("userIDpriv") != only_user_priv:
            continue

        records = entry.get("actionRecords", [])
        if records is None or len(records) == 0:
            continue

        records = sorted(records, key=lambda r: int(r.get("timestamp", 0)))
        ts = []
        for r in records:
            if "timestamp" not in r:
                continue
            try:
                ts.append(int(r["timestamp"]))
            except ValueError:
                continue

        if len(ts) == 0:
            continue

        if include_first_move:
            dts.append(0)

        if len(ts) >= 2:
            diffs = np.diff(np.array(ts, dtype=np.int64))  # consecutive deltas [web:80]
            dts.extend(diffs.tolist())

    if len(dts) == 0:
        print("No move times found for the given filters.")
        return

    dts = np.array(dts, dtype=float)

    # unit conversion
    if time_unit == "ms":
        pass
    elif time_unit == "s":
        dts = dts / 1000.0
    else:
        raise ValueError("time_unit must be 'ms' or 's'")

    # optional clipping
    if clip_min is not None:
        dts = dts[dts >= float(clip_min)]
    if clip_max is not None:
        dts = dts[dts <= float(clip_max)]

    if len(dts) == 0:
        print("All move times removed by clipping.")
        return

    user_part = "all people"
    if only_user_priv is not None:
        user_part = userPRIV_to_pub.get(only_user_priv, f"undef:{only_user_priv}")

    field_part = "all maps"
    if only_seed is not None:
        threebv = seed_3bv_lookup.get(str(only_seed), None)
        field_part = f"field {threebv} (seed {only_seed})" if threebv is not None else f"seed {only_seed}"

    plt.figure(figsize=(9, 5))
    plt.hist(dts, bins=bins, density=True, color="seagreen", edgecolor="black", alpha=0.85)  # density=True normalizes area to 1 [web:59]
    plt.xlabel(f"Time between moves ({time_unit})")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of time-to-make-a-move ({user_part}, {field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)


def plot_move_difficulty_histogram(database_entries, preprocesses, userPRIV_to_pub,
                                   only_seed=None, only_user_priv=None,
                                   bins=6,
                                   clip_min=None, clip_max=None,
                                   use_pre_action_state=True):
    """
    Histogram (density=True) of per-move difficulty, computed *per chosen action square (x,y)*
    using your snippet-style rule:

        for i, domain in enumerate(domainsArr):
            if domain[(x, y)] == domainsArr[-1][(x, y)]:
                current_move_difficulty = i

    4 modes via two optional filters:
      1) only_seed=None,  only_user_priv=None   -> all maps, all people
      2) only_seed=...,   only_user_priv=None   -> one map, all people
      3) only_seed=None,  only_user_priv=...    -> all maps, one person
      4) only_seed=...,   only_user_priv=...    -> one map, one person

    Inputs:
    - preprocesses: dict keyed by entry["_id"]["$oid"] -> action_analyses
      where action_analyses is a list of domainsArr snapshots (length usually len(actionRecords)+1)
    - domainsArr: list of domain-maps for a given step (index 0..last), last is your "most processed"

    Params:
    - bins: default 6 because your difficulty is an integer phase index (0..len(domainsArr)-1).
    - use_pre_action_state:
        True  -> use action_analyses[j] for action j (state "before" that action)
        False -> use action_analyses[j+1] for action j (state "after" that action)

    Notes:
    - Uses userIDpriv for filtering, userIDpub for plot labeling.
    - Requires global seed_3bv_lookup for nicer titles (optional).
    """
    import matplotlib.pyplot as plt
    import numpy as np

    difficulties = []

    for entry in database_entries:
        if only_seed is not None and str(entry.get("seed")) != str(only_seed): continue
        if only_user_priv is not None and entry.get("userIDpriv") != only_user_priv: continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None: continue

        action_analyses = preprocesses.get(oid, None)
        if action_analyses is None: continue

        actions = entry.get("actionRecords", [])
        if actions is None or len(actions) == 0: continue

        # Sort actions by their own timestamps so "action j" matches chronological order
        actions = sorted(actions, key=lambda r: int(r.get("timestamp", 0)))

        for j, act in enumerate(actions):
            if "x" not in act or "y" not in act: continue
            x, y = int(act["x"]), int(act["y"])

            step_idx = j if use_pre_action_state else (j + 1)
            if step_idx < 0 or step_idx >= len(action_analyses): continue

            domainsArr = action_analyses[step_idx]
            if domainsArr is None or len(domainsArr) == 0: continue

            # Need (x,y) to exist in the final (most processed) domain map
            final_domains = domainsArr[-1]
            if final_domains is None or (x, y) not in final_domains: continue

            target = final_domains[(x, y)]

            current_move_difficulty = None
            for i, domain in enumerate(domainsArr):
                if domain is None or (x, y) not in domain: continue
                if domain[(x, y)] == target:
                    current_move_difficulty = i
                    break

            if current_move_difficulty is None or current_move_difficulty == 0: continue

            difficulties.append(current_move_difficulty)

    if len(difficulties) == 0:
        print("No move difficulty values found for the given filters.")
        return

    difficulties = np.array(difficulties, dtype=float)

    if clip_min is not None: difficulties = difficulties[difficulties >= float(clip_min)]
    if clip_max is not None: difficulties = difficulties[difficulties <= float(clip_max)]

    if len(difficulties) == 0:
        print("All difficulties removed by clipping.")
        return

    user_part = "all people"
    if only_user_priv is not None:
        user_part = userPRIV_to_pub.get(only_user_priv, f"undef:{only_user_priv}")

    field_part = "all maps"
    if only_seed is not None:
        threebv = seed_3bv_lookup.get(str(only_seed), None)
        field_part = f"field {threebv} (seed {only_seed})" if threebv is not None else f"seed {only_seed}"

    # If difficulty values are small integers, set integer-ish bins by default
    if bins is None:
        max_d = int(np.max(difficulties))
        bins = np.arange(-0.5, max_d + 1.5, 1)

    plt.figure(figsize=(9, 5))
    plt.hist(difficulties, bins=bins, density=True, color="slateblue", edgecolor="black", alpha=0.55)  # density=True normalizes area to 1 [web:59]
    plt.xlabel("Move difficulty (phase index where (x,y) matches final phase)")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of move difficulty ({user_part}, {field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)

def plot_far_when_close_available(database_entries, preprocesses, userPRIV_to_pub,
                                  mode="all_people", target_user_priv=None,
                                  close_radius=1.5, far_radius=2.5,
                                  use_pre_action_state=True,
                                  ignore_first_action=True,
                                  min_events=10):
    import matplotlib.pyplot as plt
    import numpy as np

    if mode not in ("all_people", "one_person_by_map"):
        raise ValueError("mode must be 'all_people' or 'one_person_by_map'")
    if mode == "one_person_by_map" and target_user_priv is None:
        raise ValueError("target_user_priv is required for mode='one_person_by_map'")

    stats = {}  # key -> [numerator_far_when_close, denominator_close_available]

    def euclid(a, b):
        dx = float(a[0]) - float(b[0])
        dy = float(a[1]) - float(b[1])
        return float(np.sqrt(dx * dx + dy * dy))

    def move_difficulty_at_xy(domainsArr, xy):
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

    for entry in database_entries:
        user_priv = entry.get("userIDpriv")
        seed = entry.get("seed")

        if mode == "one_person_by_map" and user_priv != target_user_priv:
            continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None:
            continue
        action_analyses = preprocesses.get(oid, None)
        if action_analyses is None:
            continue

        actions = entry.get("actionRecords", [])
        if actions is None or len(actions) < 2:
            continue
        actions = sorted(actions, key=lambda r: int(r.get("timestamp", 0)))

        if mode == "all_people":
            key = user_priv
        else:
            threebv = seed_3bv_lookup.get(str(seed), None)
            key = threebv if threebv is not None else str(seed)

        if key not in stats:
            stats[key] = [0, 0]

        start_idx = 1 if ignore_first_action else 0

        for j in range(start_idx, len(actions)):
            prev = actions[j - 1]
            act = actions[j]
            if "x" not in prev or "y" not in prev or "x" not in act or "y" not in act:
                continue

            prev_xy = (int(prev["x"]), int(prev["y"]))
            chosen_xy = (int(act["x"]), int(act["y"]))

            step_idx = j if use_pre_action_state else (j + 1)
            if step_idx < 0 or step_idx >= len(action_analyses):
                continue

            domainsArr = action_analyses[step_idx]
            if domainsArr is None or len(domainsArr) == 0:
                continue
            final_domains = domainsArr[-1]
            if final_domains is None:
                continue

            # solvable coords = those with move_difficulty != 0
            solvable_coords = []
            try:
                coords_iter = final_domains.keys()
            except Exception:
                continue

            for xy in coords_iter:
                if not (isinstance(xy, tuple) and len(xy) == 2):
                    continue
                try:
                    x, y = int(xy[0]), int(xy[1])
                except Exception:
                    continue

                d = move_difficulty_at_xy(domainsArr, (x, y))
                if d is None:
                    continue
                if d != 0:
                    solvable_coords.append((x, y))

            if len(solvable_coords) == 0:
                continue

            dmin = min(euclid(prev_xy, c) for c in solvable_coords)
            if dmin > close_radius:
                continue

            d_chosen = euclid(prev_xy, chosen_xy)

            stats[key][1] += 1
            if d_chosen >= far_radius:
                stats[key][0] += 1

    keys = list(stats.keys())
    numer = np.array([stats[k][0] for k in keys], dtype=float)
    denom = np.array([stats[k][1] for k in keys], dtype=float)

    keep = denom >= float(min_events)
    keys = [k for k, ok in zip(keys, keep) if ok]
    numer = numer[keep]
    denom = denom[keep]

    if len(keys) == 0:
        print("No keys with enough events to plot (increase data or lower min_events).")
        return

    pct = (numer / denom) * 100.0

    # ---- NEW: sort by field 3bv when plotting by map ----
    if mode == "one_person_by_map":
        pairs = sorted(list(zip(keys, pct)), key=lambda t: t[0])  # sort by 3bv [web:160][web:159]
        keys = [p[0] for p in pairs]
        pct = np.array([p[1] for p in pairs], dtype=float)

    if mode == "all_people":
        labels = [userPRIV_to_pub.get(k, f"undef:{k}") for k in keys]
        title = "Percent far moves when a close solvable move existed (by person)"
        xlabel = "Person"
    else:
        labels = [str(k) for k in keys]  # keys are 3bv ints (or seed strings if missing lookup)
        who = userPRIV_to_pub.get(target_user_priv, f"undef:{target_user_priv}")
        title = f"Percent far moves when a close solvable move existed (by field 3bv) – {who}"
        xlabel = "Field (3bv)"

    plt.figure(figsize=(12, 6))
    plt.bar(labels, pct, color="teal", edgecolor="black")  # basic bar chart usage [web:143]
    plt.ylabel("Percent (%)")
    plt.xlabel(xlabel)
    plt.title(title)
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show(block=False)


def plot_hard_when_easy_available(database_entries, preprocesses, userPRIV_to_pub,
                                  mode="all_people", target_user_priv=None,
                                  hard_threshold=2,
                                  use_pre_action_state=True,
                                  ignore_first_action=True,
                                  min_events=10):
    """
    % of times chosen move was "hard" while an "easier (and no farther)" move existed.

    Easier candidate definition (relative to prev click):
      exists cand such that
        cand_difficulty < chosen_difficulty
        and dist(prev,cand) <= dist(prev,chosen)

    Denominator: steps where such a candidate exists.
    Numerator: those steps where chosen_difficulty >= hard_threshold.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    if mode not in ("all_people", "one_person_by_map"):
        raise ValueError("mode must be 'all_people' or 'one_person_by_map'")
    if mode == "one_person_by_map" and target_user_priv is None:
        raise ValueError("target_user_priv is required for mode='one_person_by_map'")

    stats = {}  # key -> [numerator, denominator]

    def euclid(a, b):
        dx = float(a[0]) - float(b[0])
        dy = float(a[1]) - float(b[1])
        return float(np.sqrt(dx * dx + dy * dy))

    def move_difficulty_at_xy(domainsArr, xy):
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

    for entry in database_entries:
        user_priv = entry.get("userIDpriv")
        seed = entry.get("seed")

        if mode == "one_person_by_map" and user_priv != target_user_priv:
            continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None:
            continue
        action_analyses = preprocesses.get(oid, None)
        if action_analyses is None:
            continue

        actions = entry.get("actionRecords", [])
        if actions is None or len(actions) < 2:
            continue
        actions = sorted(actions, key=lambda r: int(r.get("timestamp", 0)))

        if mode == "all_people":
            key = user_priv
        else:
            threebv = seed_3bv_lookup.get(str(seed), None)
            key = threebv if threebv is not None else str(seed)

        if key not in stats:
            stats[key] = [0, 0]

        start_idx = 1 if ignore_first_action else 0

        for j in range(start_idx, len(actions)):
            prev = actions[j - 1]
            act = actions[j]
            if "x" not in prev or "y" not in prev or "x" not in act or "y" not in act:
                continue

            prev_xy = (int(prev["x"]), int(prev["y"]))
            chosen_xy = (int(act["x"]), int(act["y"]))

            step_idx = j if use_pre_action_state else (j + 1)
            if step_idx < 0 or step_idx >= len(action_analyses):
                continue

            domainsArr = action_analyses[step_idx]
            if domainsArr is None or len(domainsArr) == 0:
                continue
            final_domains = domainsArr[-1]
            if final_domains is None:
                continue

            chosen_d = move_difficulty_at_xy(domainsArr, chosen_xy)
            if chosen_d is None:
                continue
            d_chosen = euclid(prev_xy, chosen_xy)

            # existence of an easier candidate that is no farther from prev
            easier_exists = False
            for xy in final_domains.keys():
                if not (isinstance(xy, tuple) and len(xy) == 2):
                    continue
                try:
                    cand_xy = (int(xy[0]), int(xy[1]))
                except Exception:
                    continue

                cand_d = move_difficulty_at_xy(domainsArr, cand_xy)
                if cand_d is None:
                    continue

                if cand_d < chosen_d and euclid(prev_xy, cand_xy) <= d_chosen:
                    easier_exists = True
                    break

            if not easier_exists:
                continue  # not in denominator

            stats[key][1] += 1
            if chosen_d >= hard_threshold:
                stats[key][0] += 1

    keys = list(stats.keys())
    numer = np.array([stats[k][0] for k in keys], dtype=float)
    denom = np.array([stats[k][1] for k in keys], dtype=float)

    keep = denom >= float(min_events)
    keys = [k for k, ok in zip(keys, keep) if ok]
    numer = numer[keep]
    denom = denom[keep]

    if len(keys) == 0:
        print("No keys with enough events to plot.")
        return

    pct = (numer / denom) * 100.0

    if mode == "one_person_by_map":
        pairs = sorted(list(zip(keys, pct)), key=lambda t: t[0])
        keys = [p[0] for p in pairs]
        pct = np.array([p[1] for p in pairs], dtype=float)

    if mode == "all_people":
        labels = [userPRIV_to_pub.get(k, f"undef:{k}") for k in keys]
        title = "Percent hard moves when an easier (and no farther) move existed (by person)"
        xlabel = "Person"
    else:
        labels = [str(k) for k in keys]
        who = userPRIV_to_pub.get(target_user_priv, f"undef:{target_user_priv}")
        title = f"Percent hard moves when an easier (and no farther) move existed (by field 3bv) – {who}"
        xlabel = "Field (3bv)"

    plt.figure(figsize=(12, 6))
    plt.bar(labels, pct, color="crimson", edgecolor="black")
    plt.ylabel("Percent (%)")
    plt.xlabel(xlabel)
    plt.title(title)
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show(block=False)



chosen_seed = reverse_seed_3bv_lookup[13]
andrei = [k for k, v in userPRIV_to_pub.items() if v == "andreiBrowser"][0]
duncan = [k for k, v in userPRIV_to_pub.items() if v == "Duncan"][0]
maxine = [k for k, v in userPRIV_to_pub.items() if v == "JazzyMaxine"][0]
one_user_priv = andrei

# THING 1.
plot_submissions_per_person(database_entries, database_entries_successful)
# plot_submissions_per_userAGENT(database_entries)
plot_submissions_per_field_3bv(database_entries, database_entries_successful)

plt.pause(0.001)
input("Press [enter] for the next set of graphs")
plt.close('all')

# THING 2,
plot_avg_solve_time_per_field(database_entries_successful)
plot_min_solve_time_per_field(database_entries_successful)


# THING 3.
test_users = [key for key, val in userPRIV_to_pub.items() if val in ["andreiBrowser", "Duncan", "Alpaca"]]
plot_avg_solve_time_per_field_per_person(database_entries_successful, test_users, userPRIV_to_pub)

plt.pause(0.001)
input("Press [enter] for the next set of graphs")
plt.close('all')

# THING 4.
for sd in [13]: # [10, 13, 22, 35, 40]:
    chosen_seed = reverse_seed_3bv_lookup[sd]
    plot_learning_curve_per_person_per_field(database_entries_successful, all_users, chosen_seed, userPRIV_to_pub, min_attempts=1)

plt.pause(0.001)
input("Press [enter] for the next set of graphs")
plt.close('all')

# THING 5.
plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None, andrei], bins=25, distance_metric="euclidean")
plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None, duncan], bins=25, distance_metric="euclidean")
plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None, maxine], bins=25, distance_metric="euclidean")

plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None] + list(userPRIV_to_pub.keys()), bins=25, distance_metric="euclidean")

plt.pause(0.001)
input("Press [enter] for the next set of graphs")
plt.close('all')


# plot_move_time_histogram(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=one_user_priv, bins=30, time_unit="s", clip_max=10)
# plot_move_time_histogram(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30, time_unit="s", clip_max=10)

plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None, maxine], bins=30, time_unit="s", clip_max=10)
plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None, duncan], bins=30, time_unit="s", clip_max=10)
plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None, andrei], bins=30, time_unit="s", clip_max=10)

plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None] + list(userPRIV_to_pub.keys()), bins=30, time_unit="s", clip_max=10)


plt.pause(0.001)
input("Press [enter] for the next set of graphs")
plt.close('all')


###################################################################################################### STUFF USING CONSTRAINT SOLVER

preprocesses = {}
for entry in database_entries:
    action_analyses = inputHandler.load_preprocessed(entry)
    if (action_analyses is None):
        print(f"ERROR: {entry=} isnt preprocessed")
        exit()

    # for i, domainsArr in enumerate(action_analyses):
    #     current_board = resimulate_partial_submission(entry, i)
    #     print(f"the game after {i} moves:")
    #     minesweeperModel.phaseRenderDomains(domainsArr, current_board)

    preprocesses[entry["_id"]["$oid"]] = action_analyses



plot_move_difficulty_histogram(database_entries, preprocesses, userPRIV_to_pub, only_seed=None, only_user_priv=one_user_priv, bins=30)
plot_move_difficulty_histogram(database_entries, preprocesses, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30)

plot_far_when_close_available(database_entries, preprocesses, userPRIV_to_pub, mode="one_person_by_map", target_user_priv=one_user_priv, close_radius=1.5, far_radius=2.5, min_events=10)
plot_far_when_close_available(database_entries, preprocesses, userPRIV_to_pub, mode="all_people", close_radius=1.5, far_radius=2.5, min_events=10)


plot_hard_when_easy_available(database_entries, preprocesses, userPRIV_to_pub, mode="one_person_by_map", target_user_priv=one_user_priv, hard_threshold=2, min_events=10)
plot_hard_when_easy_available(database_entries, preprocesses, userPRIV_to_pub, mode="all_people", hard_threshold=2, min_events=25)

plt.pause(0.001)
input("Press [enter] to terminate.")
plt.close('all')
