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

# ---------------------------- Data loading ----------------------------

database_entries = inputHandler.get_all_database_content()
database_entries_successful = list(filter(lambda entry: entry["successful"], inputHandler.get_all_database_content()))

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

def _seed_to_3bv(seed):
    return seed_3bv_lookup.get(str(seed), None)

def _seed_label(seed):
    threebv = _seed_to_3bv(seed)
    return f"field {threebv} (seed {seed})" if threebv is not None else f"seed {seed}"

def _user_label(user_priv):
    return userPRIV_to_pub.get(user_priv, f"undef:{user_priv}")

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

def _pause_step():
    plt.pause(0.001)
    input("Press [enter] for the next set of graphs")
    plt.close("all")


# ---------------------------- Graphs ----------------------------

# THING 1.
def plot_submissions_per_person(database_entries, database_entries_successful):
    """
    Bar chart: number of submissions per person (userIDpub on plot, userIDpriv internally).
    """
    plt.figure(figsize=(10, 6))

    user_ids = [entry["userIDpriv"] for entry in database_entries]
    unique_users, counts = np.unique(user_ids, return_counts=True)
    labels = [_user_label(u) for u in unique_users]
    plt.bar(labels, counts, color="red", edgecolor="black")

    user_ids = [entry["userIDpriv"] for entry in database_entries_successful]
    unique_users, counts = np.unique(user_ids, return_counts=True)
    labels = [_user_label(u) for u in unique_users]
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
        threebv = _seed_to_3bv(seed)
        if threebv is None:
            continue
        fields.append(threebv)

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
        threebv = _seed_to_3bv(seed)
        if threebv is None:
            continue
        fields.append(threebv)

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


def plot_avg_percent_difference_per_person(database_entries, userPRIV_to_pub, seed_3bv_lookup,
                                           successful_only=True, time_unit="s",
                                           min_fields_per_person=2, min_attempts_per_field=1,
                                           sort_by_metric=True):
    """
    (kept same logic; just simplified a bit)
    """
    rows = []
    for e in database_entries:
        try:
            if successful_only and not e.get("successful", False):
                continue
            seed = str(e["seed"])
            threebv = seed_3bv_lookup.get(seed, None)
            if threebv is None:
                continue

            dur = float(e["duration"])
            if time_unit == "s":
                dur /= 1000.0
            elif time_unit == "ms":
                pass
            else:
                raise ValueError("time_unit must be 's' or 'ms'")

            user_priv = e["userIDpriv"]
            rows.append((user_priv, int(threebv), dur))
        except Exception:
            continue

    if len(rows) == 0:
        print("No valid rows to compute metrics.")
        return

    users = np.array([r[0] for r in rows], dtype=object)
    fields = np.array([r[1] for r in rows], dtype=int)
    durs = np.array([r[2] for r in rows], dtype=float)

    uniq_fields, inv_f = np.unique(fields, return_inverse=True)
    global_sum = np.bincount(inv_f, weights=durs)
    global_cnt = np.bincount(inv_f)
    global_avg = global_sum / np.maximum(global_cnt, 1)
    global_avg_by_field = {int(f): float(global_avg[i]) for i, f in enumerate(uniq_fields)}

    pair_keys = np.array([f"{u}|||{fld}" for u, fld in zip(users, fields)], dtype=object)
    uniq_pairs, inv_p = np.unique(pair_keys, return_inverse=True)
    pair_sum = np.bincount(inv_p, weights=durs)
    pair_cnt = np.bincount(inv_p)
    pair_avg = pair_sum / np.maximum(pair_cnt, 1)

    user_to_diffs = {}
    for i, pair in enumerate(uniq_pairs):
        u, fld_str = pair.split("|||")
        fld = int(fld_str)
        if pair_cnt[i] < min_attempts_per_field:
            continue

        gavg = global_avg_by_field.get(fld, None)
        if gavg is None or gavg == 0:
            continue

        pdiff = 100.0 * (pair_avg[i] - gavg) / gavg
        user_to_diffs.setdefault(u, []).append(float(pdiff))

    labels = []
    metrics = []
    for u, diffs in user_to_diffs.items():
        if len(diffs) < min_fields_per_person:
            continue
        labels.append(userPRIV_to_pub.get(u, f"undef:{u}"))
        metrics.append(float(np.mean(diffs)))

    if len(metrics) == 0:
        print("No users met min_fields_per_person / min_attempts_per_field.")
        return

    labels = np.array(labels, dtype=object)
    metrics = np.array(metrics, dtype=float)

    if sort_by_metric:
        order = np.argsort(metrics)
        labels = labels[order]
        metrics = metrics[order]

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


# THING 2.
def plot_min_solve_time_per_field(database_entries):
    durations = []
    fields = []

    for entry in database_entries:
        try:
            dur = float(entry["duration"]) / 1000
            seed = entry["seed"]
            threebv = _seed_to_3bv(seed)
            if threebv is None:
                continue
            if dur < 0.05:
                continue
            if len(entry["actionRecords"]) < threebv:
                continue
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
    mins = [durations[idx == i].min() for i in range(len(unique_fields))]

    plt.figure(figsize=(10, 6))
    plt.grid(axis="y")
    plt.bar(unique_fields, mins, color="lightcoral", edgecolor="black")
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.yticks(ticks=np.arange(0, 85, step=2.5))
    plt.xlabel("Field (3bv)")
    plt.ylabel("Min solve time (s)")
    plt.title("Min solve time per field (3bv)")
    plt.tight_layout()
    plt.show(block=False)

def plot_avg_solve_time_per_field(database_entries):
    durations = []
    fields = []

    for entry in database_entries:
        try:
            dur = float(entry["duration"]) / 1000
            seed = entry["seed"]
            threebv = _seed_to_3bv(seed)
            if threebv is None:
                continue
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
    avgs = [durations[idx == i].mean() for i in range(len(unique_fields))]

    plt.figure(figsize=(10, 6))
    plt.grid(axis="y")
    plt.bar(unique_fields, avgs, color="lightcoral", edgecolor="black")
    plt.xticks(ticks=unique_fields, labels=unique_fields)
    plt.yticks(ticks=np.arange(0, 85, step=2.5))
    plt.xlabel("Field (3bv)")
    plt.ylabel("Average solve time (s)")
    plt.title("Average solve time per field (3bv)")
    plt.tight_layout()
    plt.show(block=False)


# THING 3.
def plot_avg_solve_time_per_field_per_person(database_entries, target_users, userPRIV_to_pub):
    for user in target_users:
        durations = []
        fields = []

        for entry in database_entries:
            if entry["userIDpriv"] != user:
                continue
            try:
                dur = float(entry["duration"]) / 1000
                seed = entry["seed"]
                threebv = _seed_to_3bv(seed)
                if threebv is None:
                    continue
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
    seed = field_value
    threebv = _seed_to_3bv(seed)
    if threebv is None:
        print(f"Seed {seed} not in seed_3bv_lookup.")
        return

    plt.figure(figsize=(8, 5))

    for user in target_users:
        entries = [e for e in database_entries if e["userIDpriv"] == user and str(e.get("seed", "")) == str(seed)]

        if len(entries) < min_attempts:
            print(f"Skipping {user}: only {len(entries)} attempts for field {seed}.")
            continue

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


def plot_move_distance_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30, distance_metric="euclidean", color=None):
    def dist(a, b):
        if distance_metric == "euclidean":
            return float(np.sqrt((float(a["x"]) - float(b["x"])) ** 2 + (float(a["y"]) - float(b["y"])) ** 2))
        if distance_metric == "manhattan":
            return float(abs(float(a["x"]) - float(b["x"])) + abs(float(a["y"]) - float(b["y"])))
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
    user_part = "all people" if only_user_priv is None else userPRIV_to_pub.get(only_user_priv, f"undef:{only_user_priv}")
    plt.hist(distances, bins=bins, label=user_part, density=True, color=color, edgecolor="black", alpha=0.85)

def plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None], bins=30, distance_metric="euclidean"):
    field_part = "all maps" if only_seed is None else _seed_label(only_seed)

    plt.figure(figsize=(9, 5))

    for user in users:
        plot_move_distance_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=user, bins=bins, distance_metric=distance_metric, color=None)

    plt.xlabel(f"Move distance ({distance_metric})")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of distance between moves ({field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)

def plot_move_time_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30, time_unit="s", include_first_move=False, clip_min=None, clip_max=None, color=None):
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
            diffs = np.diff(np.array(ts, dtype=np.int64))
            dts.extend(diffs.tolist())

    if len(dts) == 0:
        print("No move times found for the given filters.")
        return

    dts = np.array(dts, dtype=float)
    if time_unit == "ms":
        pass
    elif time_unit == "s":
        dts = dts / 1000.0
    else:
        raise ValueError("time_unit must be 'ms' or 's'")

    if clip_min is not None:
        dts = dts[dts >= float(clip_min)]
    if clip_max is not None:
        dts = dts[dts <= float(clip_max)]

    if len(dts) == 0:
        print("All move times removed by clipping.")
        return

    user_part = "all people" if only_user_priv is None else userPRIV_to_pub.get(only_user_priv, f"undef:{only_user_priv}")
    plt.hist(dts, label=user_part, bins=bins, density=True, edgecolor="black", alpha=0.55, color=color)

def plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None], bins=30, time_unit="s", include_first_move=False, clip_min=None, clip_max=None):
    plt.figure(figsize=(9, 5))

    for user in users:
        plot_move_time_histogram_intermediate(database_entries, userPRIV_to_pub, only_seed, user, bins, time_unit, include_first_move, clip_min, clip_max)

    field_part = "all maps" if only_seed is None else _seed_label(only_seed)
    plt.xlabel(f"Time between moves ({time_unit})")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of time-to-make-a-move ({field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.legend()
    plt.show(block=False)


# Constraint-solver plots
def plot_move_difficulty_histogram(database_entries, preprocesses, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=6, clip_min=None, clip_max=None, use_pre_action_state=True):
    difficulties = []

    for entry in database_entries:
        if only_seed is not None and str(entry.get("seed")) != str(only_seed):
            continue
        if only_user_priv is not None and entry.get("userIDpriv") != only_user_priv:
            continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None:
            continue
        action_analyses = preprocesses.get(oid, None)
        if action_analyses is None:
            continue

        actions = _sorted_actions(entry)
        if len(actions) == 0:
            continue

        for j, act in enumerate(actions):
            if "x" not in act or "y" not in act:
                continue
            x, y = int(act["x"]), int(act["y"])

            step_idx = j if use_pre_action_state else (j + 1)
            if step_idx < 0 or step_idx >= len(action_analyses):
                continue
            domainsArr = action_analyses[step_idx]
            if domainsArr is None or len(domainsArr) == 0:
                continue

            current_move_difficulty = _move_difficulty_at_xy(domainsArr, (x, y))
            if current_move_difficulty is None or current_move_difficulty == 0:
                continue

            difficulties.append(current_move_difficulty)

    if len(difficulties) == 0:
        print("No move difficulty values found for the given filters.")
        return

    difficulties = np.array(difficulties, dtype=float)
    if clip_min is not None:
        difficulties = difficulties[difficulties >= float(clip_min)]
    if clip_max is not None:
        difficulties = difficulties[difficulties <= float(clip_max)]
    if len(difficulties) == 0:
        print("All difficulties removed by clipping.")
        return

    user_part = "all people" if only_user_priv is None else _user_label(only_user_priv)
    field_part = "all maps" if only_seed is None else _seed_label(only_seed)

    if bins is None:
        max_d = int(np.max(difficulties))
        bins = np.arange(-0.5, max_d + 1.5, 1)

    plt.figure(figsize=(9, 5))
    plt.hist(difficulties, bins=bins, density=True, color="slateblue", edgecolor="black", alpha=0.55)
    plt.xlabel("Move difficulty (phase index where (x,y) matches final phase)")
    plt.ylabel("Probability density")
    plt.title(f"Distribution of move difficulty ({user_part}, {field_part})")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.show(block=False)


def plot_far_when_close_available(database_entries, preprocesses, userPRIV_to_pub, mode="all_people", target_user_priv=None, close_radius=1.5, far_radius=2.5, use_pre_action_state=True, ignore_first_action=True, min_events=10):
    if mode not in ("all_people", "one_person_by_map"):
        raise ValueError("mode must be 'all_people' or 'one_person_by_map'")
    if mode == "one_person_by_map" and target_user_priv is None:
        raise ValueError("target_user_priv is required for mode='one_person_by_map'")

    stats = {}  # key -> [numerator_far_when_close, denominator_close_available]

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

        actions = _sorted_actions(entry)
        if len(actions) < 2:
            continue

        if mode == "all_people":
            key = user_priv
        else:
            threebv = _seed_to_3bv(seed)
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

            solvable_coords = []
            for xy in final_domains.keys():
                if not (isinstance(xy, tuple) and len(xy) == 2):
                    continue
                try:
                    x, y = int(xy[0]), int(xy[1])
                except Exception:
                    continue
                d = _move_difficulty_at_xy(domainsArr, (x, y))
                if d is None:
                    continue
                if d != 0:
                    solvable_coords.append((x, y))

            if len(solvable_coords) == 0:
                continue

            dmin = min(_euclid(prev_xy, c) for c in solvable_coords)
            if dmin > close_radius:
                continue

            d_chosen = _euclid(prev_xy, chosen_xy)
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

    if mode == "one_person_by_map":
        pairs = sorted(list(zip(keys, pct)), key=lambda t: t[0])
        keys = [p[0] for p in pairs]
        pct = np.array([p[1] for p in pairs], dtype=float)

    if mode == "all_people":
        labels = [_user_label(k) for k in keys]
        title = "Percent far moves when a close solvable move existed (by person)"
        xlabel = "Person"
    else:
        labels = [str(k) for k in keys]
        who = _user_label(target_user_priv)
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


def plot_hard_when_easy_available(database_entries, preprocesses, userPRIV_to_pub, mode="all_people", target_user_priv=None, hard_threshold=2, use_pre_action_state=True, ignore_first_action=True):
    if mode not in ("all_people", "one_person_by_map"):
        raise ValueError("mode must be 'all_people' or 'one_person_by_map'")
    if mode == "one_person_by_map" and target_user_priv is None:
        raise ValueError("target_user_priv is required for mode='one_person_by_map'")

    stats = {}  # key -> [numerator, denominator]

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

        actions = _sorted_actions(entry)
        if len(actions) < 2:
            continue

        if mode == "all_people":
            key = user_priv
        else:
            threebv = _seed_to_3bv(seed)
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

            chosen_d = _move_difficulty_at_xy(domainsArr, chosen_xy)
            if chosen_d is None:
                continue
            d_chosen = _euclid(prev_xy, chosen_xy)

            easier_exists = False
            for xy in final_domains.keys():
                if not (isinstance(xy, tuple) and len(xy) == 2):
                    continue
                try:
                    cand_xy = (int(xy[0]), int(xy[1]))
                except Exception:
                    continue

                cand_d = _move_difficulty_at_xy(domainsArr, cand_xy)
                if cand_d is None:
                    continue

                if cand_d < chosen_d and _euclid(prev_xy, cand_xy) <= d_chosen:
                    easier_exists = True
                    break

            if not easier_exists:
                continue

            stats[key][1] += 1
            if chosen_d >= hard_threshold:
                stats[key][0] += 1

    keys = list(stats.keys())
    numer = np.array([stats[k][0] for k in keys], dtype=float)
    denom = np.array([stats[k][1] for k in keys], dtype=float)

    if len(keys) == 0:
        print("No keys with enough events to plot.")
        return

    pct = (numer / denom) * 100.0

    if mode == "all_people":
        labels = [_user_label(k) for k in keys]
        title = "Percent hard moves when an easier (and no farther) move existed (by person)"
        xlabel = "Person"
    else:
        pairs = sorted(list(zip(keys, pct)), key=lambda t: t[0])
        keys = [p[0] for p in pairs]
        pct = np.array([p[1] for p in pairs], dtype=float)
        labels = [str(k) for k in keys]
        who = _user_label(target_user_priv)
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


# ---------------------------- Phase runners ----------------------------

def phase_1_surface_distributions():
    plot_submissions_per_person(database_entries, database_entries_successful)
    # plot_submissions_per_userAGENT(database_entries)
    plot_submissions_per_field_3bv(database_entries, database_entries_successful)

def phase_2_time_vs_field():
    plot_avg_solve_time_per_field(database_entries_successful)
    plot_min_solve_time_per_field(database_entries_successful)

    test_users = [key for key, val in userPRIV_to_pub.items() if val in ["andreiBrowser", "Duncan", "Alpaca"]]
    plot_avg_solve_time_per_field_per_person(database_entries_successful, test_users, userPRIV_to_pub)
    plot_avg_percent_difference_per_person(database_entries, userPRIV_to_pub, seed_3bv_lookup, successful_only=True, time_unit="s")

def phase_4_learning_curves():
    for sd in [13]:  # [10, 13, 22, 35, 40]:
        chosen_seed = reverse_seed_3bv_lookup[sd]
        plot_learning_curve_per_person_per_field(database_entries_successful, all_users, chosen_seed, userPRIV_to_pub, min_attempts=1)

def phase_5_move_distance_hists():
    andrei = [k for k, v in userPRIV_to_pub.items() if v == "andreiBrowser"][0]
    duncan = [k for k, v in userPRIV_to_pub.items() if v == "Duncan"][0]
    maxine = [k for k, v in userPRIV_to_pub.items() if v == "JazzyMaxine"][0]

    plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None, andrei], distance_metric="euclidean")
    plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None, duncan], distance_metric="euclidean")
    plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None, maxine], distance_metric="euclidean")
    plot_move_distance_histogram(database_entries, userPRIV_to_pub, only_seed=None, users=[None] + list(userPRIV_to_pub.keys()), distance_metric="euclidean")

def phase_6_move_time_hists():
    andrei = [k for k, v in userPRIV_to_pub.items() if v == "andreiBrowser"][0]
    duncan = [k for k, v in userPRIV_to_pub.items() if v == "Duncan"][0]
    maxine = [k for k, v in userPRIV_to_pub.items() if v == "JazzyMaxine"][0]

    plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None, maxine], bins=30, time_unit="s", clip_max=10)
    plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None, duncan], bins=30, time_unit="s", clip_max=10)
    plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None, andrei], bins=30, time_unit="s", clip_max=10)
    plot_move_time_histogram_overlaid(database_entries, userPRIV_to_pub, only_seed=None, users=[None] + list(userPRIV_to_pub.keys()), bins=30, time_unit="s", clip_max=10)

def phase_7_constraint_solver_graphs():
    preprocesses = {}
    for entry in database_entries:
        action_analyses = inputHandler.load_preprocessed(entry)
        if action_analyses is None:
            print(f"ERROR: {entry=} isnt preprocessed")
            exit()
        preprocesses[entry["_id"]["$oid"]] = action_analyses

    andrei = [k for k, v in userPRIV_to_pub.items() if v == "andreiBrowser"][0]
    one_user_priv = andrei

    plot_move_difficulty_histogram(database_entries, preprocesses, userPRIV_to_pub, only_seed=None, only_user_priv=one_user_priv, bins=30)
    plot_move_difficulty_histogram(database_entries, preprocesses, userPRIV_to_pub, only_seed=None, only_user_priv=None, bins=30)

    plot_far_when_close_available(database_entries, preprocesses, userPRIV_to_pub,
                                  mode="one_person_by_map", target_user_priv=one_user_priv,
                                  close_radius=1.5, far_radius=2.5, min_events=0)
    plot_far_when_close_available(database_entries, preprocesses, userPRIV_to_pub,
                                  mode="all_people",
                                  close_radius=1.5, far_radius=2.5, min_events=0)

    plot_hard_when_easy_available(database_entries, preprocesses, userPRIV_to_pub,
                                  mode="one_person_by_map", target_user_priv=one_user_priv,
                                  hard_threshold=2)
    plot_hard_when_easy_available(database_entries, preprocesses, userPRIV_to_pub,
                                  mode="all_people",
                                  hard_threshold=2)


# ---------------------------- Main flow (same pauses) ----------------------------

phases = [
    phase_1_surface_distributions,
    phase_2_time_vs_field,
    phase_4_learning_curves,
    phase_5_move_distance_hists,
    phase_6_move_time_hists,
    phase_7_constraint_solver_graphs
]

for fn in phases:
    fn()
    _pause_step()
