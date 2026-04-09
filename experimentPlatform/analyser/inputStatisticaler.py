import inputHelper
import numpy as np

name_order = [] # [inputHelper._user_pub_to_priv("andreiAll"), inputHelper._user_pub_to_priv("Duncan")]
# name_order = [inputHelper._user_pub_to_priv("andreiAll"), inputHelper._user_pub_to_priv("Duncan")]

def custom_name_order(vals):
    if False: # hook to disable reordering
        return vals, list(range(len(vals)))

    new_layout = sorted(vals, key=lambda s: name_order.index(s) if s in name_order else len(vals))
    temp_vals = list(vals)
    new_positions = [temp_vals.index(val) for val in new_layout]
    return new_layout, new_positions

def rearange_name_data(xAxis, yAxis):
    _, new_indices = custom_name_order(xAxis)
    return np.array(xAxis)[new_indices], np.array(yAxis)[new_indices]



# THING 1.
def process_submissions_per_person(percentage = False):
    """
    Bar chart: number of submissions per person (userIDpub on plot, userIDpriv internally).
    """
    user_ids = [entry["userIDpriv"] for entry in inputHelper.database_entries]
    unique_users, all_counts = np.unique(user_ids, return_counts=True)

    allUser_labels = unique_users
    allUser_data = all_counts / all_counts if percentage else all_counts


    user_ids = [entry["userIDpriv"] for entry in inputHelper.database_entries_successful]
    _, counts = np.unique(user_ids, return_counts=True)

    final_counts = []
    offset = 0
    for i, user in enumerate(unique_users):
        if user in user_ids:
            final_counts.append(counts[i-offset])
        else:
            final_counts.append(0)
            offset += 1
    counts = np.array(final_counts)
    if percentage: counts = counts / all_counts

    sucUser_labels = unique_users
    sucUser_data = np.array(counts)

    # sort the data for all submissions
    allUser_labels, allUser_data = rearange_name_data(allUser_labels, allUser_data)
    allUser_labels = [inputHelper._user_label(u) for u in allUser_labels]

    # sort the data for all submissions
    sucUser_labels, sucUser_data = rearange_name_data(sucUser_labels, sucUser_data)
    sucUser_labels = [inputHelper._user_label(u) for u in sucUser_labels]

    return allUser_labels, allUser_data, sucUser_labels, sucUser_data

def process_submissions_per_userAGENT():
    """
    Bar chart: number of submissions per userAgent.
    """
    user_agents = [entry["userAgent"] for entry in inputHelper.database_entries]
    unique_agents, counts = np.unique(user_agents, return_counts=True)

    return unique_agents, counts

def process_submissions_per_field_3bv(percentage=False):
    fields = []
    for entry in inputHelper.database_entries:
        seed = entry.get("seed")
        if seed is None:
            continue
        threebv = inputHelper._seed_to_3bv(seed)
        if threebv is None:
            continue
        fields.append(threebv)

    if not fields:
        print("No valid fields (3bv) found for submissions per field.")
        return

    unique_fields, all_counts = np.unique(fields, return_counts=True)
    unique_fields1, all_counts1 = unique_fields, (all_counts/all_counts) if percentage else all_counts

    fields = []
    for entry in inputHelper.database_entries_successful:
        seed = entry.get("seed")
        if seed is None:
            continue
        threebv = inputHelper._seed_to_3bv(seed)
        if threebv is None:
            continue
        fields.append(threebv)

    if not fields:
        print("No valid fields (3bv) found for submissions per field.")
        return

    unique_fields, counts = np.unique(fields, return_counts=True)
    unique_fields2, all_counts2 = unique_fields, (counts / all_counts) if percentage else counts
    return unique_fields1, all_counts1, unique_fields2, all_counts2

def process_avg_percent_difference_per_person(successful_only=True, time_unit="s", min_fields_per_person=2, min_attempts_per_field=1, sort_by_metric=True):
    rows = []
    for e in inputHelper.database_entries:
        if successful_only and not e.get("successful", False):
            continue
        seed = str(e["seed"])
        threebv = inputHelper.seed_3bv_lookup.get(seed, None)
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
        labels.append(inputHelper._user_label(u))
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

    return labels, metrics

def process_avg_time_per_person(successful_only=True, time_unit="s", min_fields_per_person=2, min_attempts_per_field=1, sort_by_metric=True):
    rows = []
    for e in inputHelper.database_entries:
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

        pdiff = pair_avg[i]
        user_to_diffs.setdefault(u, []).append(float(pdiff))

    labels = []
    metrics = []
    for u, diffs in user_to_diffs.items():
        if len(diffs) < min_fields_per_person:
            continue
        labels.append(inputHelper._user_label(u))
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

    return labels, metrics


# THING 2.
def process_box_solve_time_per_field():
    durations = []
    fields = []

    for entry in inputHelper.database_entries_successful:
        try:
            dur = float(entry["duration"]) / 1000
            seed = entry["seed"]
            threebv = inputHelper._seed_to_3bv(seed)
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

    vals = [durations[idx == i] for i in range(len(unique_fields))]
    medianprops=dict(color="#F8982E", linewidth=2)

    avgs = [durations[idx == i].mean() for i in range(len(unique_fields))]
    avgs = [np.median(durations[idx == i]) for i in range(len(unique_fields))]

    return vals, unique_fields, medianprops, avgs

def process_avg_solve_time_per_field():
    durations = []
    fields = []

    for entry in inputHelper.database_entries:
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

    return unique_fields, avgs


# THING 3.
def process_avg_solve_time_per_field_per_person(target_users):
    returnable = []
    for user in target_users:
        durations = []
        fields = []

        for entry in inputHelper.database_entries_successful:
            if entry["userIDpriv"] != user:
                continue
            try:
                dur = float(entry["duration"]) / 1000
                seed = entry["seed"]
                threebv = inputHelper._seed_to_3bv(seed)
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
        times = [durations[idx == i] for i in range(len(unique_fields))]
        avg_times = [durations[idx == i].mean() for i in range(len(unique_fields))]

        returnable.append([times, unique_fields, avg_times])
    return returnable

# VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV

# THING 4.
def process_learning_curve_per_person_per_field(target_users, field_value, min_attempts=3, block=False):
    seed = field_value
    threebv = inputHelper._seed_to_3bv(seed)
    if threebv is None:
        print(f"Seed {seed} not in seed_3bv_lookup.")
        return

    returnable = []
    for user in target_users:
        entries = [e for e in inputHelper.database_entries_successful if e["userIDpriv"] == user and str(e.get("seed", "")) == str(seed)]

        if len(entries) < min_attempts:
            print(f"Skipping {user}: only {len(entries)} attempts for field {seed}.")
            continue

        entries.sort(key=lambda x: int(x["timestamp"]))
        durations = [float(x["duration"]) for x in entries]
        attempts = list(range(1, len(durations) + 1))

        returnable.append((attempts, durations))
    return returnable

def process_move_distance_histogram_intermediate(only_seed=None, only_user_priv=None, bins=30, distance_metric="euclidean", color=None):
    def dist(a, b):
        if distance_metric == "euclidean":
            return float(np.sqrt((float(a["x"]) - float(b["x"])) ** 2 + (float(a["y"]) - float(b["y"])) ** 2))
        if distance_metric == "manhattan":
            return float(abs(float(a["x"]) - float(b["x"])) + abs(float(a["y"]) - float(b["y"])))
        raise ValueError(f"Unknown distance_metric={distance_metric}")

    distances = []
    for entry in inputHelper.database_entries:
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
    return distances

def process_move_time_histogram_intermediate(only_seed=None, only_user_priv=None, bins=30, time_unit="s", include_first_move=False, clip_min=None, clip_max=None, color=None):
    dts = []
    for entry in inputHelper.database_entries:
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

    return dts

def process_avg_move_time_per_user_intermediate(only_seed=None, only_user_priv=None, time_unit="s", include_first_move=False, clip_min=None, clip_max=None):
    """
    Returns (label, avg_time) for a single user/seed filter, or None if no data.
    """
    dts = []
    for entry in inputHelper.database_entries:
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
            dts.extend(np.diff(np.array(ts, dtype=np.int64)).tolist())

    if len(dts) == 0:
        return None

    dts = np.array(dts, dtype=float)
    if time_unit == "s":
        dts = dts / 1000.0
    elif time_unit != "ms":
        raise ValueError("time_unit must be 'ms' or 's'")

    if clip_min is not None:
        dts = dts[dts >= float(clip_min)]
    if clip_max is not None:
        dts = dts[dts <= float(clip_max)]

    if len(dts) == 0:
        return None

    label = "all people" if only_user_priv is None else only_user_priv
    return label, float(np.mean(dts))


def process_avg_move_time_per_user(only_seed=None, users=[None], time_unit="s", include_first_move=False, clip_min=None, clip_max=None, user_order=None):
    results = []
    for user in [u for u in users if u is not None]:
        r = process_avg_move_time_per_user_intermediate(only_seed, user, time_unit, include_first_move, clip_min, clip_max)
        if r is not None:
            results.append(r)

    # append "all people" (None) last if it was in users
    if None in users:
        r = process_avg_move_time_per_user_intermediate(only_seed, None, time_unit, include_first_move, clip_min, clip_max)
        if r is not None:
            results.append(r)

    if not results:
        print("No move time data found.")
        return

    labels = [r[0] for r in results]
    data   = [r[1] for r in results]

    labels, data = rearange_name_data(labels, data)
    labels = [inputHelper._user_label(u) for u in labels]

    return labels, data

def process_avg_time_per_difficulty_level(max_difficulty_level=3, time_unit="s", use_pre_action_state=True, successful_only=True, min_moves_per_level=1):
    """
    For each person, compute their average move time at each difficulty level (1..max_difficulty_level).

    Difficulty of a move is computed with inputHelper.movedifficultyat_xy(domainsArr, (x,y)).
    Moves with difficulty 0 or None are ignored.
    Time for a move = delta between consecutive action timestamps within a submission.

    Returns:
      labels_pub: list of userIDpub strings
      times_by_level: dict level(int) -> np.array of avg times per user (same order as labels_pub),
                      entries with fewer than min_moves_per_level for that level become np.nan
    """
    # user_priv -> level -> list of dt values
    user_level_times = {}

    for entry in inputHelper.database_entries:
        if successful_only and not entry.get("successful", False):
            continue

        user_priv = entry.get("userIDpriv")
        if user_priv is None:
            continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None:
            continue
        action_analyses = inputHelper.preprocesses.get(oid, None)
        if action_analyses is None:
            continue

        # actions = inputHelper.sortedactions(entry)
        # if len(actions) < 2:
        #     continue
        actions = entry["actionRecords"]

        # collect timestamps and actions in sorted order
        ts = []
        valid_actions = []
        for act in actions:
            ts_val = int(act["timestamp"])
            ts.append(ts_val)
            valid_actions.append(act)

        if len(ts) < 2:
            continue

        ts = np.array(ts, dtype=np.int64)
        dts = np.diff(ts)  # len = len(valid_actions) - 1

        for j in range(1, len(valid_actions)):
            prev_act = valid_actions[j - 1]
            act = valid_actions[j]

            if "x" not in act or "y" not in act:
                continue
            x, y = int(act["x"]), int(act["y"])

            step_idx = j if use_pre_action_state else (j + 1)
            if step_idx < 0 or step_idx >= len(action_analyses):
                continue
            domainsArr = action_analyses[step_idx]
            if domainsArr is None or len(domainsArr) == 0:
                continue

            d = inputHelper._move_difficulty_at_xy(domainsArr, (x, y))
            if d is None or d <= 0:
                continue

            if d > max_difficulty_level:
                continue

            dt = float(dts[j - 1])  # ms
            if time_unit == "s":
                dt /= 1000.0
            elif time_unit == "ms":
                pass
            else:
                raise ValueError("time_unit must be 'ms' or 's'")

            user_level_times.setdefault(user_priv, {}).setdefault(d, []).append(dt)

    if not user_level_times:
        print("No difficulty/time data found.")
        return [], {}

    # build ordered user list
    users_priv = list(user_level_times.keys())

    times_by_level = {}
    for level in range(1, max_difficulty_level + 1):
        vals = []
        for u in users_priv:
            arr = user_level_times.get(u, {}).get(level, [])
            if len(arr) < min_moves_per_level:
                vals.append(np.nan)
            else:
                vals.append(float(np.mean(arr)))
        times_by_level[level] = np.array(vals, dtype=float)


    _, times_by_level[1] = rearange_name_data(users_priv, times_by_level[1])
    _, times_by_level[2] = rearange_name_data(users_priv, times_by_level[2])
    users_priv, times_by_level[3] = rearange_name_data(users_priv, times_by_level[3])

    labels = [inputHelper._user_label(u) for u in users_priv]

    return labels, times_by_level

def process_move_difficulty_histogram(only_seed=None, only_user_priv=None, bins=6, clip_min=None, clip_max=None, use_pre_action_state=True):
    difficulties = []

    for entry in inputHelper.database_entries:
        if only_seed is not None and str(entry.get("seed")) != str(only_seed):
            continue
        if only_user_priv is not None and entry.get("userIDpriv") != only_user_priv:
            continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None:
            continue
        action_analyses = inputHelper.preprocesses.get(oid, None)
        if action_analyses is None:
            continue

        actions = inputHelper._sorted_actions(entry)
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

            current_move_difficulty = inputHelper._move_difficulty_at_xy(domainsArr, (x, y))
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

    if bins is None:
        max_d = int(np.max(difficulties))
        bins = np.arange(-0.5, max_d + 1.5, 1)

    return difficulties, bins


def process_far_when_close_available(mode="all_people", target_user_priv=None, close_radius=1.5, far_radius=2.5, use_pre_action_state=True, ignore_first_action=True, min_events=10):
    if mode not in ("all_people", "one_person_by_map"):
        raise ValueError("mode must be 'all_people' or 'one_person_by_map'")
    if mode == "one_person_by_map" and target_user_priv is None:
        raise ValueError("target_user_priv is required for mode='one_person_by_map'")

    stats = {}  # key -> [numerator_far_when_close, denominator_close_available]

    for entry in inputHelper.database_entries:
        user_priv = entry.get("userIDpriv")
        seed = entry.get("seed")

        if mode == "one_person_by_map" and user_priv != target_user_priv:
            continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None:
            continue
        action_analyses = inputHelper.preprocesses.get(oid, None)
        if action_analyses is None:
            continue

        actions = inputHelper._sorted_actions(entry)
        if len(actions) < 2:
            continue

        if mode == "all_people":
            key = user_priv
        else:
            threebv = inputHelper._seed_to_3bv(seed)
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
                d = inputHelper._move_difficulty_at_xy(domainsArr, (x, y))
                if d is None:
                    continue
                if d != 0:
                    solvable_coords.append((x, y))

            if len(solvable_coords) == 0:
                continue

            dmin = min(inputHelper._euclid(prev_xy, c) for c in solvable_coords)
            if dmin > close_radius:
                continue

            d_chosen = inputHelper._euclid(prev_xy, chosen_xy)
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
        keys, pct = rearange_name_data(keys, pct)
        labels = [inputHelper._user_label(k) for k in keys]
        title = "Percent far moves when a close solvable move existed (by person)"
        xlabel = "Person"
    else:
        keys, pct = rearange_name_data(keys, pct)
        labels = [str(k) for k in keys]
        who = inputHelper._user_label(target_user_priv)
        title = f"Percent far moves when a close solvable move existed (by field 3bv) – {who}"
        xlabel = "Field (3bv)"

    return labels, pct


def process_hard_when_easy_available(mode="all_people", target_user_priv=None, hard_threshold=2, use_pre_action_state=True, ignore_first_action=True):
    if mode not in ("all_people", "one_person_by_map"):
        raise ValueError("mode must be 'all_people' or 'one_person_by_map'")
    if mode == "one_person_by_map" and target_user_priv is None:
        raise ValueError("target_user_priv is required for mode='one_person_by_map'")

    stats = {}  # key -> [numerator, denominator]

    for entry in inputHelper.database_entries:
        user_priv = entry.get("userIDpriv")
        seed = entry.get("seed")

        if mode == "one_person_by_map" and user_priv != target_user_priv:
            continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None:
            continue
        action_analyses = inputHelper.preprocesses.get(oid, None)
        if action_analyses is None:
            continue

        actions = inputHelper._sorted_actions(entry)
        if len(actions) < 2:
            continue

        if mode == "all_people":
            key = user_priv
        else:
            threebv = inputHelper._seed_to_3bv(seed)
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

            chosen_d = inputHelper._move_difficulty_at_xy(domainsArr, chosen_xy)
            if chosen_d is None:
                continue
            d_chosen = inputHelper._euclid(prev_xy, chosen_xy)

            easier_exists = False
            for xy in final_domains.keys():
                if not (isinstance(xy, tuple) and len(xy) == 2):
                    continue
                try:
                    cand_xy = (int(xy[0]), int(xy[1]))
                except Exception:
                    continue

                cand_d = inputHelper._move_difficulty_at_xy(domainsArr, cand_xy)
                if cand_d is None:
                    continue

                if cand_d < chosen_d and inputHelper._euclid(prev_xy, cand_xy) <= d_chosen:
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
        keys, pct = rearange_name_data(keys, pct)
        labels = [inputHelper._user_label(k) for k in keys]
        title = "Percent hard moves when an easier (and no farther) move existed (by person)"
        xlabel = "Person"
    else:
        pairs = sorted(list(zip(keys, pct)), key=lambda t: t[0])
        keys = [p[0] for p in pairs]
        pct = np.array([p[1] for p in pairs], dtype=float)
        labels = [str(k) for k in keys]
        who = inputHelper._user_label(target_user_priv)
        title = f"Percent hard moves when an easier (and no farther) move existed (by field 3bv) – {who}"
        xlabel = "Field (3bv)"

    return labels, pct

# THING 8(?).
def process_avg_move_difficulty_per_map(use_pre_action_state=True, ignore_difficulty0=True, require_in_final_domain=True, min_moves=50):
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

    # seed -> accumulators
    sum_by_seed = {}
    cnt_by_seed = {}
    subs_by_seed = {}

    for entry in inputHelper.database_entries_successful:
        seed = str(entry.get("seed", ""))
        if seed == "":
            continue

        oid = entry.get("_id", {}).get("$oid", None)
        if oid is None:
            continue
        action_analyses = inputHelper.preprocesses.get(oid, None)
        if action_analyses is None:
            continue

        actions = entry.get("actionRecords", [])
        if actions is None or len(actions) == 0:
            continue
        actions = sorted(actions, key=lambda r: int(r.get("timestamp", 0)))

        any_move_counted = False

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

            if require_in_final_domain:
                final_domains = domainsArr[-1]
                if final_domains is None or (x, y) not in final_domains:
                    continue

            d = move_difficulty_at_xy(domainsArr, (x, y))
            if d is None:
                continue
            if ignore_difficulty0 and d == 0:
                continue

            sum_by_seed[seed] = sum_by_seed.get(seed, 0.0) + float(d)
            cnt_by_seed[seed] = cnt_by_seed.get(seed, 0) + 1
            any_move_counted = True

        if any_move_counted:
            subs_by_seed[seed] = subs_by_seed.get(seed, 0) + 1

    out = {}
    for seed, s in sum_by_seed.items():
        n = cnt_by_seed.get(seed, 0)
        if n <= 0:
            continue
        out[seed] = {
            "threebv": inputHelper.seed_3bv_lookup.get(str(seed), None),
            "avg_difficulty": float(s) / float(n),
            "n_moves": int(n),
            "n_submissions": int(subs_by_seed.get(seed, 0)),
        }


    rows = []
    for seed, d in out.items():
        if d["n_moves"] < min_moves:
            continue
        x = d["threebv"]
        if x is None:
            continue
        rows.append((int(x), float(d["avg_difficulty"]), seed, int(d["n_moves"])))

    if len(rows) == 0:
        print("No maps met min_moves (or missing 3bv).")
        return

    rows.sort(key=lambda t: t[0])
    x = [r[0] for r in rows]
    y = [r[1] for r in rows]
    return x, y

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

def process_avg_entropy_per_field_for_user(target_user_priv, use_pre_action_state=True, successful_only=False):
    """
    Bar chart for a single user: x = field (3bv), y = avg entropy across all their submissions on that field.
    Entropy per submission = mean log2(possible_moves) across its actions.
    """

    def submission_avg_entropy(entry, action_analyses, hints):
        actions = inputHelper._sorted_actions(entry)
        if not actions:
            return None
        entropies = []
        for j in range(len(actions)):
            step_idx = j if use_pre_action_state else (j + 1)
            if step_idx < 0 or step_idx >= len(action_analyses):
                continue
            domainsArr = action_analyses[step_idx]
            if domainsArr is None or len(domainsArr) == 0:
                continue
            n = find_possible_moves(domainsArr, hints)
            if n <= 0:
                continue
            entropies.append(np.log2(n))
        return float(np.mean(entropies)) if entropies else None

    field_to_entropies = {}

    for entry in inputHelper.database_entries:
        if entry.get("userIDpriv") != target_user_priv:
            continue
        if successful_only and not entry.get("successful", False):
            continue

        threebv = inputHelper._seed_to_3bv(entry.get("seed"))
        if threebv is None:
            continue

        oid = entry.get("_id", {}).get("$oid")
        if oid is None:
            continue
        action_analyses = inputHelper.preprocesses.get(oid)
        if action_analyses is None:
            continue

        hints = inputHelper.get_hints(entry)
        if hints is None:
            continue

        e = submission_avg_entropy(entry, action_analyses, hints)
        if e is None:
            continue

        field_to_entropies.setdefault(int(threebv), []).append(e)

    if not field_to_entropies:
        print(f"No entropy data for user {inputHelper._user_label(target_user_priv)}.")
        return

    sorted_fields = sorted(field_to_entropies.keys())
    avg_entropies = [float(np.mean(field_to_entropies[f])) for f in sorted_fields]

    return [str(f) for f in sorted_fields], avg_entropies

def process_avg_entropy_per_user(use_pre_action_state=True, successful_only=False, sort_descending=True, data_only=False):
    """
    Bar chart: one bar per user, y = avg entropy across all their submissions (all fields pooled).
    Entropy per submission = mean log2(possible_moves) across its actions.
    """

    def submission_avg_entropy(entry, action_analyses, hints):
        actions = inputHelper._sorted_actions(entry)
        if not actions:
            return None
        entropies = []
        for j in range(len(actions)):
            step_idx = j if use_pre_action_state else (j + 1)
            if step_idx < 0 or step_idx >= len(action_analyses):
                continue
            domainsArr = action_analyses[step_idx]
            if domainsArr is None or len(domainsArr) == 0:
                continue
            n = find_possible_moves(domainsArr, hints)
            if n <= 0:
                continue
            entropies.append(np.log2(n))
        return float(np.mean(entropies)) if entropies else None

    user_to_entropies = {}

    for entry in inputHelper.database_entries:
        if successful_only and not entry.get("successful", False): continue

        user_priv = entry.get("userIDpriv")
        if user_priv is None: continue

        oid = entry.get("_id", {}).get("$oid")
        if oid is None: continue
        action_analyses = inputHelper.preprocesses.get(oid)
        if action_analyses is None: continue

        hints = inputHelper.get_hints(entry)
        if hints is None: continue

        e = submission_avg_entropy(entry, action_analyses, hints)
        if e is None: continue
        user_to_entropies.setdefault(user_priv, []).append(e)

    if not user_to_entropies:
        print("No entropy data found for entry", entry)
        return

    users = list(user_to_entropies.keys())
    data = [float(np.mean(user_to_entropies[u])) for u in users]

    # labels = [inputHelper._user_label(u) for u in users]

    users, data = rearange_name_data(users, data)
    labels = [inputHelper._user_label(u) for u in users]

    # if sort_descending:
    #     order = np.argsort(avgs)[::-1]
    #     labels = [labels[i] for i in order]
    #     avgs = [avgs[i] for i in order]

    return labels, data

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
