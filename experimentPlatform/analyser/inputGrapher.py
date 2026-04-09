import inputHandler
import inputHelper
import inputStatisticaler
import minesweeperModel
import solverAlgs

import matplotlib.pyplot as plt
import numpy as np

# andrei = [k for k, v in inputHelper.userPRIV_to_pub.items() if v == "andreiAll"][0]
# # andrei = [k for k, v in inputHelper.userPRIV_to_pub.items() if v == "andreiBrowser"][0]
# duncan = [k for k, v in inputHelper.userPRIV_to_pub.items() if v == "Duncan"][0]
# maxine = [k for k, v in inputHelper.userPRIV_to_pub.items() if v == "JazzyMaxine"][0]
# alpaca = [k for k, v in inputHelper.userPRIV_to_pub.items() if v == "Alpaca"][0]

inputStatisticaler.name_order = [ inputHelper._user_pub_to_priv(n) for n in inputStatisticaler.process_avg_entropy_per_user(use_pre_action_state=True, successful_only=False, sort_descending=True, data_only=True)[0]]

# ---------------------------- Phase runners ----------------------------

def plot_submissions_per_person(percentage = False):
    """
    Bar chart: number of submissions per person (userIDpub on plot, userIDpriv internally).
    """
    plt.figure(figsize=(10, 6))

    labels1, data1, labels2, data2 = inputStatisticaler.process_submissions_per_person(percentage=percentage)

    plt.bar(labels1, data1, label="all submissions", color="red", edgecolor="black")
    plt.bar(labels2, data2, label="successful only", color="green", edgecolor="black")

    plt.xlabel("User")
    plt.ylabel("Number of submissions")
    plt.title("Distribution of submissions per person" + (" (percentages successful)" if percentage else ""))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)

def plot_submissions_per_userAGENT():
    """
    Bar chart: number of submissions per userAgent.
    """
    unique_agents, counts = inputStatisticaler.process_submissions_per_userAGENT()

    plt.figure(figsize=(10, 6))
    plt.bar(unique_agents, counts, color="skyblue", edgecolor="black")
    plt.xlabel("UserAgent")
    plt.ylabel("Number of submissions")
    plt.title("Distribution of submissions per userAgent")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show(block=False)

def plot_submissions_per_field_3bv(percentage=False):
    """
    Bar chart: number of submissions per field (x axis = 3bv, via seed_3bv_lookup).
    """
    plt.figure(figsize=(10, 6))

    unique_fields1, counts1, unique_fields2, counts2 = inputStatisticaler.process_submissions_per_field_3bv(percentage)
    plt.bar(unique_fields1, counts1, label="all submissions", color="red", edgecolor="black")
    plt.bar(unique_fields2, counts2, label="successful only", color="green", edgecolor="black")

    plt.xlabel("Field (3bv)")
    plt.ylabel("Number of submissions")
    plt.title("Distribution of submissions per field (3bv)")
    plt.xticks(ticks=unique_fields2, labels=unique_fields2)
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)

def plot_avg_percent_difference_per_person(successful_only=True, time_unit="s", min_fields_per_person=2, min_attempts_per_field=1, sort_by_metric=True):
    labels, metrics = inputStatisticaler.process_avg_percent_difference_per_person(successful_only, time_unit, min_fields_per_person, min_attempts_per_field, sort_by_metric)

    plt.figure(figsize=(12, 6))
    plt.bar(labels, metrics, color="royalblue", edgecolor="black")
    plt.axhline(0, color="black", linewidth=1)
    plt.ylabel(f"Avg % difference vs global ({time_unit})")
    plt.xlabel("Person")
    plt.title("Avg percent difference from global field averages (lower is faster)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)

def plot_avg_time_per_person(successful_only=True, time_unit="s", min_fields_per_person=2, min_attempts_per_field=1, sort_by_metric=True):
    labels, metrics = inputStatisticaler.process_avg_time_per_person(successful_only, time_unit, min_fields_per_person, min_attempts_per_field, sort_by_metric)

    plt.figure(figsize=(12, 6))
    plt.bar(labels, metrics, color="royalblue", edgecolor="black")
    plt.axhline(0, color="black", linewidth=1)
    plt.ylabel(f"Avg map solve time ({time_unit})")
    plt.xlabel("Person")
    plt.title("Avg field times per person")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)


# THING 2.
def plot_box_solve_time_per_field():
    vals, unique_fields, medianprops, avgs = inputStatisticaler.process_box_solve_time_per_field()

    plt.figure(figsize=(10, 6))
    plt.grid(axis="y")

    plt.boxplot(vals, positions=unique_fields, medianprops=medianprops)
    plt.bar(unique_fields, avgs, color="lightcoral", edgecolor="black")

    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.xlabel("Field (3bv)")
    plt.ylabel("Min solve time (s)")
    plt.title("solve time per field (3bv)")
    plt.tight_layout()
    plt.show(block=False)

def plot_avg_solve_time_per_field():
    unique_fields, avgs = inputStatisticaler.process_avg_solve_time_per_field()

    plt.figure(figsize=(10, 6))
    plt.grid(axis="y")
    plt.bar(unique_fields, avgs, color="lightcoral", edgecolor="black")
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.yticks(ticks=np.arange(0, 85, step=2.5))
    plt.xlabel("Field (3bv)")
    plt.ylabel("Average solve time (s)")
    plt.title("Average solve time per field (3bv)")

    plt.margins(0)
    plt.tight_layout()
    plt.show(block=False)


# THING 3.
def plot_avg_solve_time_per_field_per_person(target_users):
        results = inputStatisticaler.process_avg_solve_time_per_field_per_person(target_users)

        for result, user in zip(results, target_users):
            plt.figure(figsize=(8, 5))
            times, unique_fields, avg_times = result
            plt.boxplot(times, positions=unique_fields)
            plt.bar(unique_fields, avg_times, color="mediumpurple", edgecolor="black")
            plt.xticks(ticks=unique_fields, labels=unique_fields)
            plt.xlabel("Field (3bv)")
            plt.ylabel("Average solve time (s)")
            plt.title(f"Average solve time per field - {inputHelper._user_label(user)}")
            plt.tight_layout()
            plt.show(block=False)

# VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV

# THING 4.
def plot_learning_curve_per_person_per_field(target_users, field_value, min_attempts=3, block=False):
    plt.figure(figsize=(8, 5))

    results = inputStatisticaler.process_learning_curve_per_person_per_field(target_users, field_value, min_attempts, block)

    for result, user in zip(results, target_users):
        attempts, durations = result
        plt.plot(attempts, durations, linestyle="-", label=f"{inputHelper._user_label(user)}")

    plt.xlabel("Attempt number")
    plt.ylabel("Solve time (ms)")
    plt.title(f"Learning curves of different users for field with 3bv {field_value}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.legend()
    plt.show(block=block)


def plot_move_distance_histogram(only_seed=None, users=[None], bins=30, distance_metric="euclidean"):
    field_part = "all maps" if only_seed is None else inputHelper._seed_label(only_seed)

    plt.figure(figsize=(9, 5))

    avgs = []
    labels = []
    for user in users:
        result = inputStatisticaler.process_move_distance_histogram_intermediate(only_seed=None, only_user_priv=user, bins=bins, distance_metric=distance_metric)
        if result is None: continue

        # user_part = "all people" if user is None else inputHelper._user_label(user)
        user_part = "all people" if user is None else user
        avgs.append(np.mean(result))
        labels.append(user_part)
        # plt.hist(result, bins=bins, label=user_part, density=True, edgecolor="black", alpha=0.85)

    labels, avgs = inputStatisticaler.rearange_name_data(labels, avgs)
    labels = [inputHelper._user_label(u) for u in labels]

    print(f"{labels=}")
    print(f"{avgs=}")
    
    
    plt.bar(labels, avgs, edgecolor="black", alpha=0.85)
    plt.xticks(rotation=45, ha="right")

    plt.xlabel(f"Move distance ({distance_metric})")
    plt.ylabel("Probability density")
    plt.ylim(0, 3)
    plt.title(f"Distribution of distance between moves ({field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)

def plot_move_time_histogram_overlaid(only_seed=None, users=[None], bins=30, time_unit="s", include_first_move=False, clip_min=None, clip_max=None):
    plt.figure(figsize=(9, 5))


    avgs = []
    labels = []
    for user in users:
        dts = inputStatisticaler.process_move_time_histogram_intermediate(only_seed, user, bins, time_unit, include_first_move, clip_min, clip_max)
        if dts is None: continue

        # user_part = "all people" if user is None else inputHelper._user_label(user)
        user_part = "all people" if user is None else user

        avgs.append(np.mean(dts))
        labels.append(user_part)
        # plt.hist(dts, label=user_part, bins=bins, density=True, edgecolor="black", alpha=0.55)

    labels, avgs = inputStatisticaler.rearange_name_data(labels, avgs)
    labels = [inputHelper._user_label(u) for u in labels]

    plt.bar(labels, avgs, edgecolor="black", alpha=0.55)
    plt.xticks(rotation=45, ha="right")

    field_part = "all maps" if only_seed is None else inputHelper._seed_label(only_seed)
    plt.xlabel(f"Time between moves ({time_unit})")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of time-to-make-a-move ({field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.ylim(0, 3.7)
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)


def plot_avg_move_time_per_user(only_seed=None, users=[None], time_unit="s", include_first_move=False, clip_min=None, clip_max=None):
    labels, data = inputStatisticaler.process_avg_move_time_per_user(only_seed, users, time_unit, include_first_move, clip_min, clip_max)

    field_part = "all maps" if only_seed is None else inputHelper._seed_label(only_seed)
    plt.figure(figsize=(9, 5))
    plt.bar(labels, data, color="steelblue", edgecolor="black")
    plt.xlabel("User")
    plt.ylabel(f"Avg time between moves ({time_unit})")
    plt.title(f"Average time between moves ({field_part})")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)

def plot_avg_time_per_difficulty_level(max_difficulty_level=3, time_unit="s", use_pre_action_state=True, successful_only=True, min_moves_per_level=1):
    """
    Scatter plot: for each person, their avg move time at difficulty levels 1,2,3.
    x-axis = person, three dots per person:
      level 1 = blue, level 2 = green, level 3 = yellow.
    """
    labels, times_by_level = inputStatisticaler.process_avg_time_per_difficulty_level(max_difficulty_level=max_difficulty_level, time_unit=time_unit, use_pre_action_state=use_pre_action_state, successful_only=successful_only, min_moves_per_level=min_moves_per_level,
    )
    if not labels or not times_by_level:
        return

    x = np.arange(len(labels))

    plt.figure(figsize=(12, 6))

    if 1 in times_by_level:
        # _, times_by_level[1] = inputStatisticaler.rearange_name_data(labels, times_by_level[1])

        plt.scatter(x, times_by_level[1], color="blue", label="difficulty 1")
    if 2 in times_by_level and max_difficulty_level >= 2:
        # _, times_by_level[2] = inputStatisticaler.rearange_name_data(labels, times_by_level[2])

        plt.scatter(x, times_by_level[2], color="green", label="difficulty 2")
    if 3 in times_by_level and max_difficulty_level >= 3:
        # _, times_by_level[3] = inputStatisticaler.rearange_name_data(labels, times_by_level[3])

        plt.scatter(x, times_by_level[3], color="yellow", edgecolors="black", label="difficulty 3")


    labels, x = inputStatisticaler.rearange_name_data(labels, x)
    print(x)
    plt.xticks(ticks=x, labels=labels, rotation=45, ha="right")
    plt.xlabel("Person")
    plt.ylabel(f"Avg time between moves ({time_unit})")
    plt.title("Average move time by difficulty level per person")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)


def plot_move_difficulty_histogram(only_seed=None, only_user_priv=None, bins=6, clip_min=None, clip_max=None, use_pre_action_state=True):
    difficulties, bins = inputStatisticaler.process_move_difficulty_histogram(only_seed, only_user_priv, bins, clip_min, clip_max, use_pre_action_state)

    user_part = "all people" if only_user_priv is None else inputHelper._user_label(only_user_priv)
    field_part = "all maps" if only_seed is None else inputHelper._seed_label(only_seed)

    plt.figure(figsize=(9, 5))
    plt.hist(difficulties, bins=bins, density=True, color="slateblue", edgecolor="black", alpha=0.55)
    plt.xlabel("Move difficulty (phase index where (x,y) matches final phase)")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of move difficulty ({user_part}, {field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)


def plot_far_when_close_available(mode="all_people", target_user_priv=None, close_radius=1.5, far_radius=2.5, use_pre_action_state=True, ignore_first_action=True, min_events=10):
    labels, pct = inputStatisticaler.process_far_when_close_available(mode, target_user_priv, close_radius, far_radius, use_pre_action_state, ignore_first_action, min_events)

    if mode == "all_people":
        title = "Percent far moves when a close solvable move existed (by person)"
        xlabel = "Person"
    else:
        who = inputHelper._user_label(target_user_priv)
        title = f"Percent far moves when a close solvable move existed (by field 3bv) – {who}"
        xlabel = "Field (3bv)"

    plt.figure(figsize=(12, 6))
    plt.bar(labels, pct, color="teal", edgecolor="black")
    plt.ylabel("Percent (%)")
    plt.xlabel(xlabel)
    plt.title(title)
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show(block=False)


def plot_hard_when_easy_available(mode="all_people", target_user_priv=None, hard_threshold=2, use_pre_action_state=True, ignore_first_action=True):
    labels, pct = inputStatisticaler.process_hard_when_easy_available(mode, target_user_priv, hard_threshold, use_pre_action_state, ignore_first_action)

    if mode == "all_people":
        title = "Percent hard moves when an easier (and no farther) move existed (by person)"
        xlabel = "Person"
    else:
        who = inputHelper._user_label(target_user_priv)
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

# THING 8(?).
def plot_avg_move_difficulty_per_map(use_pre_action_state=True, min_moves=50):
    x, y = inputStatisticaler.process_avg_move_difficulty_per_map(use_pre_action_state, min_moves)

    plt.figure(figsize=(10, 5))
    plt.bar(x, y, color="slateblue", edgecolor="black")
    plt.xlabel("Field (3bv)")
    plt.ylabel("Avg move difficulty")
    plt.title("Average move difficulty per map (across all actions)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)

def plot_avg_entropy_per_field_for_user(target_user_priv, use_pre_action_state=True, successful_only=False):
    """
    Bar chart for a single user: x = field (3bv), y = avg entropy across all their submissions on that field.
    Entropy per submission = mean log2(possible_moves) across its actions.
    """
    thing1, avg_entropies = inputStatisticaler.process_avg_entropy_per_field_for_user(target_user_priv, use_pre_action_state, successful_only)

    plt.figure(figsize=(10, 5))
    plt.bar(thing1, avg_entropies, color="darkorange", edgecolor="black")
    plt.xlabel("Field (3bv)")
    plt.ylabel("Avg reward")
    plt.title(f"Avg move reward per field – {inputHelper._user_label(target_user_priv)}")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)

def plot_avg_entropy_per_user(use_pre_action_state=True, successful_only=False, sort_descending=True, data_only=False):
    """
    Bar chart: one bar per user, y = avg entropy across all their submissions (all fields pooled).
    Entropy per submission = mean log2(possible_moves) across its actions.
    """

    labels, avgs = inputStatisticaler.process_avg_entropy_per_user(use_pre_action_state, successful_only, sort_descending, data_only)

    plt.figure(figsize=(10, 5))
    plt.bar(labels, avgs, color="steelblue", edgecolor="black")
    plt.xlabel("User")
    plt.ylabel("Avg reward")
    plt.title("Avg move reward per user across all submissions")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def phase_1_surface_distributions():
    plot_submissions_per_person(percentage=False)
    plot_submissions_per_field_3bv(percentage = False)
    plot_submissions_per_person(percentage=True)
    plot_submissions_per_field_3bv(percentage = True)

def phase_2_time_vs_field():
    plot_box_solve_time_per_field()

    # test_users = [andrei, duncan, alpaca]
    # plot_avg_solve_time_per_field_per_person(test_users)
    plot_avg_percent_difference_per_person(successful_only=True, time_unit="s")

def phase_4_learning_curves():
    # for sd in  [13]:  # [10, 13, 22, 35, 40]:
    for sd in inputHelper.reverse_seed_3bv_lookup:
        chosen_seed = inputHelper.reverse_seed_3bv_lookup[sd]
        plot_learning_curve_per_person_per_field(inputHelper.all_users, chosen_seed, min_attempts=1, block=False)

def phase_5_move_distance_hists():
    # plot_move_distance_histogram(only_seed=None, users=[None, andrei], distance_metric="euclidean")
    # plot_move_distance_histogram(only_seed=None, users=[None, duncan], distance_metric="euclidean")
    # plot_move_distance_histogram(only_seed=None, users=[None, maxine], distance_metric="euclidean")
    plot_move_distance_histogram(only_seed=None, users=[None] + list(inputHelper.userPRIV_to_pub.keys()), distance_metric="euclidean")

def phase_6_move_time_hists():
    # plot_move_time_histogram_overlaid(only_seed=None, users=[None, maxine], bins=30, time_unit="s", clip_max=10)
    # plot_move_time_histogram_overlaid(only_seed=None, users=[None, duncan], bins=30, time_unit="s", clip_max=10)
    # plot_move_time_histogram_overlaid(only_seed=None, users=[None, andrei], bins=30, time_unit="s", clip_max=10)
    plot_move_time_histogram_overlaid(only_seed=None, users=[None] + list(inputHelper.userPRIV_to_pub.keys()), bins=30, time_unit="s", clip_max=10)

    plot_avg_move_time_per_user(only_seed=None, users=[None] + list(inputHelper.userPRIV_to_pub.keys()), time_unit="s", clip_max=10)
    plot_avg_time_per_difficulty_level()

def phase_7_constraint_solver_graphs():
    # one_user_priv = andrei

    # plot_move_difficulty_histogram(only_seed=None, only_user_priv=one_user_priv, bins=30)
    plot_move_difficulty_histogram(only_seed=None, only_user_priv=None, bins=30)

    # plot_far_when_close_available(mode="one_person_by_map", target_user_priv=one_user_priv, close_radius=1.5, far_radius=2.5, min_events=0)
    plot_far_when_close_available(mode="all_people", close_radius=1.5, far_radius=2.5, min_events=0)

    # plot_hard_when_easy_available(mode="one_person_by_map", target_user_priv=one_user_priv, hard_threshold=2)
    plot_hard_when_easy_available(mode="all_people", hard_threshold=2)

def phase_8_map_average_experienced_difficulty():
    plot_avg_move_difficulty_per_map()

def phase_9_entropy_stuff():
    # plot_avg_entropy_per_field_for_user(andrei, use_pre_action_state=True, successful_only=False)
    plot_avg_entropy_per_user(use_pre_action_state=True, successful_only=False, sort_descending=True)

# ---------------------------- Main flow (same pauses) ----------------------------

phases = [
    phase_1_surface_distributions,
    phase_2_time_vs_field,
    # phase_4_learning_curves,
    phase_5_move_distance_hists,
    phase_6_move_time_hists,
    phase_7_constraint_solver_graphs,
    phase_8_map_average_experienced_difficulty,
    phase_9_entropy_stuff,
]

phase = 0
while phase is not None:
    phases[phase]()

    plt.pause(0.001)
    phases_reprs = ", ".join([f"{i}: {f.__name__}" for i, f in enumerate(phases)])
    print("\nwas just on phase", phases[phase].__name__)
    response = input(f"[enter]: next set of graphs\nq: quit\n{phases_reprs}\n")
    plt.close("all")

    if response == "": phase += 1
    elif response == "q": break
    else: phase = int(response)
