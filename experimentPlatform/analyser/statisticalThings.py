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

reverse_seed_3bv_lookup = {
    2 : "1769089904946",
    5 : "1769089890419",
    7 : "1769089890390",
    8 : "1769089890393",
    9 : "1769089890402",
    10: "1769089890404",
    11: "1769089890406",
    12: "1769089890426",
    13: "1769089890391",
    14: "1769089890380",
    15: "1769089890394",
    16: "1769089890387",
    17: "1769089890388",
    18: "1769089890444",
    19: "1769089890461",
    20: "1769089890420",
    22: "1769089890408",
    26: "1769089890446",
    30: "1769089890521",
    35: "1769089891879",
    40: "1769089892886",
}

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


######################################################### STUFF NOT USING CONSTRAINT SOLVER.. JUST SURFACE LEVEL STATISTICS

database_entries = inputHandler.get_all_database_content()

# Build userIDpriv → userIDpub mapping once
all_users = list(set([entry["userIDpriv"] for entry in database_entries]))
userPRIV_to_pub = {}
for neededID in all_users[::-1]:
    userPRIV_to_pub[neededID] = f"undef:{neededID}"
    for entry in database_entries:
        if entry["userIDpriv"] == neededID:
            userPRIV_to_pub[neededID] = entry["userIDpub"]
            # break # actually.. dont break, so that the last public username is used instead of the first one found.


# THING 1.
def plot_submissions_per_person(database_entries):
    """
    Bar chart: number of submissions per person (userIDpub on plot, userIDpriv internally).
    """
    user_ids = [entry["userIDpriv"] for entry in database_entries]
    unique_users, counts = np.unique(user_ids, return_counts=True)

    # Map priv IDs to pub names for labels
    labels = [userPRIV_to_pub[u] for u in unique_users]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color="skyblue", edgecolor="black")
    plt.xlabel("User")
    plt.ylabel("Number of submissions")
    plt.title("Distribution of submissions per person")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
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


def plot_submissions_per_field_3bv(database_entries):
    """
    Bar chart: number of submissions per field (x axis = 3bv, via seed_3bv_lookup).
    """
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

    plt.figure(figsize=(10, 6))
    plt.bar(unique_fields, counts, color="orange", edgecolor="black")
    plt.xlabel("Field (3bv)")
    plt.ylabel("Number of submissions")
    plt.title("Distribution of submissions per field (3bv)")
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.tight_layout()
    plt.show(block=False)


plot_submissions_per_person(database_entries)
plot_submissions_per_userAGENT(database_entries)
plot_submissions_per_field_3bv(database_entries)


# THING 2.
def plot_avg_solve_time_per_field(database_entries):
    """
    Bar chart: average solve time (duration) per field (x axis = 3bv, via seed_3bv_lookup).
    Only successful runs are considered.
    """
    durations = []
    fields = []

    for entry in database_entries:
        try:
            if not entry["successful"]:
                continue
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


plot_avg_solve_time_per_field(database_entries)


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


test_users = [key for key, val in userPRIV_to_pub.items() if val in ["andreiBrowser", "Duncan", "Alpaca"]]
print(f"{all_users=}")
print(f"{test_users=}")
plot_avg_solve_time_per_field_per_person(database_entries, test_users, userPRIV_to_pub)


# THING 4.
def plot_learning_curve_per_person_per_field(
    database_entries,
    target_users,
    field_value,
    userPRIV_to_pub,
    min_attempts=3,
):
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


for sd in [13]: # [10, 13, 22, 35, 40]:
    chosen_seed = reverse_seed_3bv_lookup[sd]
    plot_learning_curve_per_person_per_field(database_entries, all_users, chosen_seed, userPRIV_to_pub, min_attempts=1)


plt.pause(0.001)
input("Press [enter] to continue.")
exit()




###################################################################################################### STUFF USING CONSTRAINT SOLVER
testEntry = inputHandler.get_database_entry("7478532506737.593", "1770053639277", "1769089890391")
print(testEntry)

print("DA BOARD")
print(inputHandler.board_generate(9, 9, 10, testEntry["seed"]))

print(testEntry["actionRecords"])
for i in range(len(testEntry["actionRecords"])+1): # i is an index, but resimulate takes a count
    print(f"the game after {i} moves:")
    current_board = inputHandler.resimulate_partial_submission(testEntry, i)
    print()

    domain = minesweeperModel.create_domains(current_board)
    constraints, variableToConstraints, constraintsToVariables = minesweeperModel.build_constraints(current_board, domain)

    domain = solverAlgs.generalizedArcConsistency(domain, constraints, variableToConstraints, constraintsToVariables, current_board)

    minesweeperModel.renderDomains(domain, current_board)
