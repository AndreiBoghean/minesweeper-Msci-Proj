import inputHandler
import inputHelper
import inputStatisticaler
import minesweeperModel
import solverAlgs

import matplotlib.pyplot as plt
import numpy as np

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
    plt.title("Distribution of submissions per person" + " (percentages successful)" if percentage else "")
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

# VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV

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
            times, unique_fields, avg_times = result

            plt.figure(figsize=(8, 5))

            plt.boxplot(times, positions=unique_fields)
            plt.bar(unique_fields, avg_times, color="mediumpurple", edgecolor="black")

            plt.xticks(ticks=unique_fields, labels=unique_fields)
            plt.xlabel("Field (3bv)")
            plt.ylabel("Average solve time (s)")
            plt.title(f"Average solve time per field – {inputHelper._user_label(user)}")
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

    test_users = [key for key, val in inputHelper.userPRIV_to_pub.items() if val in ["andreiAll", "Duncan", "Alpaca"]]
    plot_avg_solve_time_per_field_per_person(test_users)
    plot_avg_percent_difference_per_person(successful_only=True, time_unit="s")

def phase_4_learning_curves():
    for sd in  [13]:  # [10, 13, 22, 35, 40]:
    # for sd in reverse_seed_3bv_lookup:
        chosen_seed = reverse_seed_3bv_lookup[sd]
        inputStatisticaler.plot_learning_curve_per_person_per_field(all_users, chosen_seed, userPRIV_to_pub, min_attempts=1, block=False)

def phase_5_move_distance_hists():
    andrei = [k for k, v in userPRIV_to_pub.items() if v == "andreiAll"][0]
    duncan = [k for k, v in userPRIV_to_pub.items() if v == "Duncan"][0]
    maxine = [k for k, v in userPRIV_to_pub.items() if v == "JazzyMaxine"][0]

    inputStatisticaler.plot_move_distance_histogram(userPRIV_to_pub, only_seed=None, users=[None, andrei], distance_metric="euclidean")
    inputStatisticaler.plot_move_distance_histogram(userPRIV_to_pub, only_seed=None, users=[None, duncan], distance_metric="euclidean")
    inputStatisticaler.plot_move_distance_histogram(userPRIV_to_pub, only_seed=None, users=[None, maxine], distance_metric="euclidean")
    inputStatisticaler.plot_move_distance_histogram(userPRIV_to_pub, only_seed=None, users=[None] + list(userPRIV_to_pub.keys()), distance_metric="euclidean")

def phase_6_move_time_hists():
    andrei = [k for k, v in userPRIV_to_pub.items() if v == "andreiAll"][0]
    duncan = [k for k, v in userPRIV_to_pub.items() if v == "Duncan"][0]
    maxine = [k for k, v in userPRIV_to_pub.items() if v == "JazzyMaxine"][0]

    inputStatisticaler.plot_move_time_histogram_overlaid(userPRIV_to_pub, only_seed=None, users=[None, maxine], bins=30, time_unit="s", clip_max=10)
    inputStatisticaler.plot_move_time_histogram_overlaid(userPRIV_to_pub, only_seed=None, users=[None, duncan], bins=30, time_unit="s", clip_max=10)
    inputStatisticaler.plot_move_time_histogram_overlaid(userPRIV_to_pub, only_seed=None, users=[None, andrei], bins=30, time_unit="s", clip_max=10)
    inputStatisticaler.plot_move_time_histogram_overlaid(userPRIV_to_pub, only_seed=None, users=[None] + list(userPRIV_to_pub.keys()), bins=30, time_unit="s", clip_max=10)

    inputStatisticaler.plot_avg_move_time_per_user(userPRIV_to_pub, only_seed=None, users=[None] + list(userPRIV_to_pub.keys()), time_unit="s", clip_max=10)

def phase_7_constraint_solver_graphs():
    andrei = [k for k, v in userPRIV_to_pub.items() if v == "andreiAll"][0]
    one_user_priv = andrei

    inputStatisticaler.plot_move_difficulty_histogram(tries, preprocesses, userPRIV_to_pub, only_seed=None, only_user_priv=one_user_priv, bins=30)
    inputStatisticaler.plot_move_difficulty_histogram(preprocesses, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30)

    inputStatisticaler.plot_far_when_close_available(preprocesses, userPRIV_to_pub,
                                  mode="one_person_by_map", target_user_priv=one_user_priv,
                                  close_radius=1.5, far_radius=2.5, min_events=0)
    inputStatisticaler.plot_far_when_close_available(preprocesses, userPRIV_to_pub,
                                  mode="all_people",
                                  close_radius=1.5, far_radius=2.5, min_events=0)

    inputStatisticaler.plot_hard_when_easy_available(preprocesses, userPRIV_to_pub,
                                  mode="one_person_by_map", target_user_priv=one_user_priv,
                                  hard_threshold=2)
    inputStatisticaler.plot_hard_when_easy_available(preprocesses, userPRIV_to_pub,
                                  mode="all_people",
                                  hard_threshold=2)

def phase_8_map_average_experienced_difficulty():
    inputStatisticaler.plot_avg_move_difficulty_per_map(preprocesses, seed_3bv_lookup)

def phase_9_entropy_stuff():
    andrei = [k for k, v in userPRIV_to_pub.items() if v == "andreiAll"][0]
    inputStatisticaler.plot_avg_entropy_per_field_for_user(preprocesses, andrei, use_pre_action_state=True, successful_only=False)
    inputStatisticaler.plot_avg_entropy_per_user(preprocesses, use_pre_action_state=True, successful_only=False, sort_descending=True)

# ---------------------------- Main flow (same pauses) ----------------------------

phases = [
    phase_1_surface_distributions,
    phase_2_time_vs_field,
    phase_4_learning_curves,
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
