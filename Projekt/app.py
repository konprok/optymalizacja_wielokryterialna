import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import openpyxl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import os
import zipfile

def load_resources(resources_path):
    with open(resources_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_games(games_path):
    with open(games_path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_owners(owners_value):
    if isinstance(owners_value, int):
        return owners_value
    if isinstance(owners_value, float):
        return int(owners_value)
    if not isinstance(owners_value, str):
        return 0
    val = owners_value.strip()
    if "-" in val:
        parts = val.split("-")
        if len(parts) == 2:
            try:
                low = int(parts[0].replace(",", ""))
                high = int(parts[1].replace(",", ""))
                return (low + high) // 2
            except:
                return 0
    else:
        try:
            return int(val.replace(",", ""))
        except:
            return 0
    return 0

def parse_price(price_value):
    if isinstance(price_value, (int, float)):
        return float(price_value)
    if isinstance(price_value, str):
        try:
            return float(price_value)
        except:
            return 0.0
    return 0.0

def game_matches_preferences(game_info, preferences):
    max_price = preferences.get("max_price")
    if max_price is not None:
        price_val = parse_price(game_info.get("price", 999999))
        if price_val > max_price:
            return False
    min_total_reviews = preferences.get("min_total_reviews", 0)
    pos = game_info.get("positive", 0)
    neg = game_info.get("negative", 0)
    total_rev = pos + neg
    if total_rev < min_total_reviews:
        return False
    min_pos = preferences.get("min_positive_ratio", 0.0)
    ratio = pos / total_rev if total_rev > 0 else 0.0
    if ratio < min_pos:
        return False
    mand_sub = preferences.get("mandatory_sub_lang", "")
    if mand_sub:
        if mand_sub not in game_info.get("supported_languages", []):
            return False
    req_plat = preferences.get("required_platforms", [])
    for rp in req_plat:
        if not game_info.get(rp.lower(), False):
            return False
    return True

def compute_score_saw(game_info, preferences):
    w_pos = preferences.get("weight_positive_ratio", 0.0)
    w_price = preferences.get("weight_price", 0.0)
    w_audio = preferences.get("weight_audio_lang", 0.0)
    w_owners = preferences.get("weight_owners", 0.0)
    w_med = preferences.get("weight_med_time", 0.0)
    w_tags = preferences.get("weight_tags", 0.0)
    pos = game_info.get("positive", 0)
    neg = game_info.get("negative", 0)
    tot = pos + neg
    ratio = pos / tot if tot > 0 else 0.0
    price = parse_price(game_info.get("price", 0))
    w_price_adj = 0.2 * w_price
    pref_audio = preferences.get("preferred_audio_lang", "")
    full_audio = game_info.get("full_audio_languages", [])
    audio_val = 1.0 if (pref_audio and pref_audio in full_audio) else 0.0
    owners_raw = parse_owners(game_info.get("estimated_owners", "0")) * 0.2
    owners_log = math.log(owners_raw + 1, 10) if owners_raw > 0 else 0.0
    med_time = game_info.get("median_playtime_forever", 0)
    max_min = 6000.0
    med_norm = med_time / max_min if med_time < max_min else 1.0
    game_tags = game_info.get("tags", {})
    pref_tags = preferences.get("preferred_tags", [])
    matched = sum(1 for t in pref_tags if t in game_tags)
    frac_tags = matched / len(pref_tags) if pref_tags else 0.0
    score = 0.0
    score += w_pos * ratio
    score += w_price_adj * price
    score += w_audio * audio_val
    score += w_owners * owners_log
    score += w_med * med_norm
    score += w_tags * frac_tags
    return score

def recommend_games_saw(games_data, preferences, top_n=10, played_game_ids=set()):
    filtered = []
    for gid, info in games_data.items():
        if gid in played_game_ids:
            continue
        if game_matches_preferences(info, preferences):
            filtered.append((gid, info))
    if not filtered:
        return []
    scored = []
    for (gid, info) in filtered:
        sc = compute_score_saw(info, preferences)
        scored.append((gid, sc))
    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[:top_n]
    results = []
    for (gid, sc) in best:
        info = games_data[gid]
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        tot = pos + neg
        ratio = round(pos / tot, 2) if tot > 0 else 0.0
        price = parse_price(info.get("price", 0))
        results.append({
            "id": gid,
            "name": info.get("name", ""),
            "score": round(sc, 3),
            "price": price,
            "pos_percentage": ratio,
            "total_reviews": tot,
            "required_age": info.get("required_age", 0),
            "estimated_owners": parse_owners(info.get("estimated_owners", "0")),
            "median_playtime_forever": info.get("median_playtime_forever", 0),
        })
    return results

def recommend_games_topsis(games_data, preferences, top_n=10, played_game_ids=set()):
    candidate_games = []
    for gid, info in games_data.items():
        if gid in played_game_ids:
            continue
        if game_matches_preferences(info, preferences):
            candidate_games.append((gid, info))
    if not candidate_games:
        return []
    w_pos = preferences.get("weight_positive_ratio", 0.0)
    w_price = abs(preferences.get("weight_price", 0.0))
    w_audio = preferences.get("weight_audio_lang", 0.0)
    w_owners = preferences.get("weight_owners", 0.0)
    w_med = preferences.get("weight_med_time", 0.0)
    w_tags = preferences.get("weight_tags", 0.0)
    sum_w = w_pos + w_price + w_audio + w_owners + w_med + w_tags
    if sum_w < 1e-9:
        sum_w = 1.0
    cost_benefit = [False, True, False, False, False, False]
    data_matrix = []
    game_ids = []
    pref_audio = preferences.get("preferred_audio_lang", "")
    pref_tags = preferences.get("preferred_tags", [])
    for (gid, info) in candidate_games:
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        tot = pos + neg
        ratio = pos / tot if tot > 0 else 0.0
        price = parse_price(info.get("price", 0))
        full_audio = info.get("full_audio_languages", [])
        audio_val = 1.0 if (pref_audio and pref_audio in full_audio) else 0.0
        ow_raw = parse_owners(info.get("estimated_owners", "0")) * 0.2
        owners_log = math.log(ow_raw + 1, 10) if ow_raw > 0 else 0.0
        med_time = info.get("median_playtime_forever", 0)
        max_min = 6000.0
        med_norm = med_time / max_min if med_time < max_min else 1.0
        game_tags = info.get("tags", {})
        matched = sum(1 for t in pref_tags if t in game_tags)
        frac_tags = matched / len(pref_tags) if pref_tags else 0.0
        row = [ratio, price, audio_val, owners_log, med_norm, frac_tags]
        data_matrix.append(row)
        game_ids.append(gid)
    rows = len(data_matrix)
    cols = 6
    if rows == 0:
        return []
    col_sumsq = [0.0] * cols
    for r in range(rows):
        for c in range(cols):
            col_sumsq[c] += data_matrix[r][c]**2
    for r in range(rows):
        for c in range(cols):
            if col_sumsq[c] > 1e-12:
                data_matrix[r][c] /= math.sqrt(col_sumsq[c])
            else:
                data_matrix[r][c] = 0.0
    w_array = [
        w_pos / sum_w,
        w_price / sum_w,
        w_audio / sum_w,
        w_owners / sum_w,
        w_med / sum_w,
        w_tags / sum_w
    ]
    for r in range(rows):
        for c in range(cols):
            data_matrix[r][c] *= w_array[c]
    ideal = [0.0] * cols
    anti_ideal = [0.0] * cols
    for c in range(cols):
        col_vals = [data_matrix[r][c] for r in range(rows)]
        if cost_benefit[c] == False:
            ideal[c] = max(col_vals)
            anti_ideal[c] = min(col_vals)
        else:
            ideal[c] = min(col_vals)
            anti_ideal[c] = max(col_vals)
    distances = []
    for r in range(rows):
        dist_plus = 0.0
        dist_minus = 0.0
        for c in range(cols):
            dist_plus += (data_matrix[r][c] - ideal[c])**2
            dist_minus += (data_matrix[r][c] - anti_ideal[c])**2
        dist_plus = math.sqrt(dist_plus)
        dist_minus = math.sqrt(dist_minus)
        ci = dist_minus / (dist_plus + dist_minus) if (dist_plus + dist_minus) > 1e-12 else 0.0
        distances.append(ci)
    combined = list(zip(game_ids, distances))
    combined.sort(key=lambda x: x[1], reverse=True)
    best = combined[:top_n]
    results = []
    for (gid, sc) in best:
        info = games_data[gid]
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        tot = pos + neg
        ratio = round(pos / tot, 2) if tot > 0 else 0.0
        price = parse_price(info.get("price", 0))
        results.append({
            "id": gid,
            "name": info.get("name", ""),
            "score": round(sc, 3),
            "price": price,
            "pos_percentage": ratio,
            "total_reviews": tot,
            "estimated_owners": parse_owners(info.get("estimated_owners", "0")),
            "median_playtime_forever": info.get("median_playtime_forever", 0)
        })
    return results

def recommend_games_wpm(games_data, preferences, top_n=10, played_game_ids=set()):
    candidate_games = []
    for gid, info in games_data.items():
        if gid in played_game_ids:
            continue
        if game_matches_preferences(info, preferences):
            candidate_games.append((gid, info))
    if not candidate_games:
        return []
    w_pos = preferences.get("weight_positive_ratio", 0.0)
    w_price = abs(preferences.get("weight_price", 0.0))
    w_audio = preferences.get("weight_audio_lang", 0.0)
    w_owners = preferences.get("weight_owners", 0.0)
    w_med = preferences.get("weight_med_time", 0.0)
    w_tags = preferences.get("weight_tags", 0.0)
    sum_w = w_pos + w_price + w_audio + w_owners + w_med + w_tags
    if sum_w < 1e-9:
        sum_w = 1.0
    cost_benefit = [False, True, False, False, False, False]
    data_matrix = []
    game_ids = []
    pref_audio = preferences.get("preferred_audio_lang", "")
    pref_tags = preferences.get("preferred_tags", [])
    for (gid, info) in candidate_games:
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        tot = pos + neg
        ratio = pos / tot if tot > 0 else 0.0
        price = parse_price(info.get("price", 0))
        full_audio = info.get("full_audio_languages", [])
        audio_val = 1.0 if (pref_audio and pref_audio in full_audio) else 0.0
        ow_raw = parse_owners(info.get("estimated_owners", "0")) * 0.2
        owners_log = math.log(ow_raw + 1, 10) if ow_raw > 0 else 0.0
        med_time = info.get("median_playtime_forever", 0)
        max_min = 6000.0
        med_norm = med_time / max_min if med_time < max_min else 1.0
        game_tags = info.get("tags", {})
        matched = sum(1 for t in pref_tags if t in game_tags)
        frac_tags = matched / len(pref_tags) if pref_tags else 0.0
        row = [ratio, price, audio_val, owners_log, med_norm, frac_tags]
        data_matrix.append(row)
        game_ids.append(gid)
    rows = len(data_matrix)
    cols = 6
    if rows == 0:
        return []
    col_min = [float("inf")] * cols
    col_max = [0.0] * cols
    for r in range(rows):
        for c in range(cols):
            val = data_matrix[r][c]
            if val < col_min[c]:
                col_min[c] = val
            if val > col_max[c]:
                col_max[c] = val
    norm_matrix = []
    for r in range(rows):
        row_norm = []
        for c in range(cols):
            val = data_matrix[r][c]
            if cost_benefit[c] == False:
                denom = col_max[c] if col_max[c] > 1e-12 else 1e-12
                row_norm.append(val / denom)
            else:
                nom = col_min[c] if col_min[c] < float("inf") else 1e-12
                if val > 1e-12:
                    row_norm.append(nom / val)
                else:
                    row_norm.append(0.0)
        norm_matrix.append(row_norm)
    w_rel = [
        w_pos / sum_w,
        w_price / sum_w,
        w_audio / sum_w,
        w_owners / sum_w,
        w_med / sum_w,
        w_tags / sum_w
    ]
    scored = []
    for r in range(rows):
        sum_log = 0.0
        for c in range(cols):
            valn = norm_matrix[r][c]
            if valn < 1e-12:
                sum_log = -9999999.0
                break
            sum_log += w_rel[c] * math.log(valn)
        score = math.exp(sum_log) if sum_log > -9999999.0 else 0.0
        scored.append((game_ids[r], score))
    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[:top_n]
    results = []
    for (gid, sc) in best:
        info = games_data[gid]
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        tot = pos + neg
        ratio = round(pos / tot, 2) if tot > 0 else 0.0
        p = parse_price(info.get("price", 0))
        results.append({
            "id": gid,
            "name": info.get("name", ""),
            "score": round(sc, 3),
            "price": p,
            "pos_percentage": ratio,
            "total_reviews": tot,
            "estimated_owners": parse_owners(info.get("estimated_owners", "0")),
            "median_playtime_forever": info.get("median_playtime_forever", 0)
        })
    return results

def recommend_games_vikor(games_data, preferences, top_n=10, played_game_ids=set()):
    candidate_games = []
    for gid, info in games_data.items():
        if gid in played_game_ids:
            continue
        if game_matches_preferences(info, preferences):
            candidate_games.append((gid, info))
    if not candidate_games:
        return []
    w_pos = preferences.get("weight_positive_ratio", 0.0)
    w_price = abs(preferences.get("weight_price", 0.0))
    w_audio = preferences.get("weight_audio_lang", 0.0)
    w_owners = preferences.get("weight_owners", 0.0)
    w_med = preferences.get("weight_med_time", 0.0)
    w_tags = preferences.get("weight_tags", 0.0)
    sum_w = w_pos + w_price + w_audio + w_owners + w_med + w_tags
    if sum_w < 1e-9:
        sum_w = 1.0
    cost_benefit = [False, True, False, False, False, False]
    pref_audio = preferences.get("preferred_audio_lang", "")
    pref_tags = preferences.get("preferred_tags", [])
    data_matrix = []
    game_ids = []
    for (gid, info) in candidate_games:
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        tot = pos + neg
        ratio = pos / tot if tot > 0 else 0.0
        price = parse_price(info.get("price", 0))
        full_audio = info.get("full_audio_languages", [])
        audio_val = 1.0 if (pref_audio and pref_audio in full_audio) else 0.0
        ow_raw = parse_owners(info.get("estimated_owners", "0")) * 0.2
        owners_log = math.log(ow_raw + 1, 10) if ow_raw > 0 else 0.0
        med_time = info.get("median_playtime_forever", 0)
        max_min = 6000.0
        med_norm = med_time / max_min if med_time < max_min else 1.0
        game_tags = info.get("tags", {})
        matched = sum(1 for t in pref_tags if t in game_tags)
        frac_tags = matched / len(pref_tags) if pref_tags else 0.0
        row = [ratio, price, audio_val, owners_log, med_norm, frac_tags]
        data_matrix.append(row)
        game_ids.append(gid)
    rows = len(data_matrix)
    cols = 6
    if rows == 0:
        return []
    f_star = [0.0] * cols
    f_minus = [0.0] * cols
    for c in range(cols):
        col_vals = [data_matrix[r][c] for r in range(rows)]
        if cost_benefit[c] == False:
            f_star[c] = max(col_vals)
            f_minus[c] = min(col_vals)
        else:
            f_star[c] = min(col_vals)
            f_minus[c] = max(col_vals)
    w_rel = [
        w_pos / sum_w,
        w_price / sum_w,
        w_audio / sum_w,
        w_owners / sum_w,
        w_med / sum_w,
        w_tags / sum_w
    ]
    S_list = []
    R_list = []
    for r in range(rows):
        S_val = 0.0
        R_val = 0.0
        for c in range(cols):
            diff_num = abs(f_star[c] - data_matrix[r][c])
            diff_den = abs(f_star[c] - f_minus[c]) if abs(f_star[c] - f_minus[c]) > 1e-12 else 1.0
            local_frac = diff_num / diff_den
            local_val = w_rel[c] * local_frac
            S_val += local_val
            if local_val > R_val:
                R_val = local_val
        S_list.append(S_val)
        R_list.append(R_val)
    S_star, S_minus = min(S_list), max(S_list)
    R_star, R_minus = min(R_list), max(R_list)
    v = 0.5
    Q_list = []
    for i in range(rows):
        si = S_list[i]
        ri = R_list[i]
        FS = (si - S_star) / (S_minus - S_star) if (S_minus - S_star) > 1e-12 else 0.0
        FR = (ri - R_star) / (R_minus - R_star) if (R_minus - R_star) > 1e-12 else 0.0
        Qi = v * FS + (1.0 - v) * FR
        Q_list.append(Qi)
    combined = list(zip(game_ids, Q_list))
    combined.sort(key=lambda x: x[1], reverse=False)
    best = combined[:top_n]
    results = []
    for (gid, Qv) in best:
        info = games_data[gid]
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        tot = pos + neg
        ratio = round(pos / tot, 2) if tot > 0 else 0.0
        price = parse_price(info.get("price", 0))
        results.append({
            "id": gid,
            "name": info.get("name", ""),
            "score": round(Qv, 4),
            "price": price,
            "pos_percentage": ratio,
            "total_reviews": tot,
            "estimated_owners": parse_owners(info.get("estimated_owners", "0")),
            "median_playtime_forever": info.get("median_playtime_forever", 0)
        })
    return results

class GameRecommenderApp(tk.Tk):
    def __init__(self, resources_data, games_data):
        super().__init__()
        self.title("Game Recommender (Scalona aplikacja)")
        self.geometry("1300x950")
        self.all_subtitle_langs = resources_data["languages"]
        self.all_audio_langs = resources_data["audio_languages"]
        self.all_tags = resources_data["tags"]
        self.games_data = games_data
        self.played_game_ids = set()
        self.selected_tags = []
        self.recommended_games_for_plot = []
        self.build_gui()

    def build_gui(self):
        left_frame = tk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        tk.Label(left_frame, text="Wyszukaj grę po nazwie:").pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.search_var, width=30).pack(fill=tk.X, pady=5)
        tk.Button(left_frame, text="Szukaj", command=self.search_games).pack(pady=5)
        self.search_results_list = tk.Listbox(left_frame, height=15, width=50)
        self.search_results_list.pack(fill=tk.BOTH, expand=True)
        self.search_results_list.bind("<<ListboxSelect>>", self.show_game_details)
        tk.Button(left_frame, text="Dodaj do ogranych", command=self.add_to_played).pack(pady=5)
        tk.Label(left_frame, text="Gry ograne:").pack(anchor=tk.W, pady=(10, 0))
        self.played_games_list = tk.Listbox(left_frame, height=10, width=50)
        self.played_games_list.pack(fill=tk.BOTH, expand=True)
        tk.Button(left_frame, text="Usuń z ogranych", command=self.remove_from_played).pack(pady=5)
        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        method_frame = tk.LabelFrame(right_frame, text="Metoda wielokryterialna")
        method_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(method_frame, text="Wybierz metodę:").grid(row=0, column=0, sticky=tk.W)
        self.method_var = tk.StringVar(value="SAW")
        self.method_combo = ttk.Combobox(method_frame, textvariable=self.method_var,
                                         values=["SAW", "TOPSIS", "WPM", "VIKOR"],
                                         state="readonly", width=15)
        self.method_combo.grid(row=0, column=1, sticky=tk.W)
        prefs_frame = tk.LabelFrame(right_frame, text="Filtry twarde")
        prefs_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(prefs_frame, text="Maks. cena:").grid(row=0, column=0, sticky=tk.W)
        self.max_price_var = tk.DoubleVar(value=100.0)
        tk.Entry(prefs_frame, textvariable=self.max_price_var, width=6).grid(row=0, column=1, sticky=tk.W)
        tk.Label(prefs_frame, text="Min. liczba recenzji:").grid(row=1, column=0, sticky=tk.W)
        self.min_reviews_var = tk.IntVar(value=10000)
        tk.Entry(prefs_frame, textvariable=self.min_reviews_var, width=6).grid(row=1, column=1, sticky=tk.W)
        tk.Label(prefs_frame, text="Min. % pozytywnych (0..1):").grid(row=2, column=0, sticky=tk.W)
        self.min_pos_ratio_var = tk.DoubleVar(value=0.75)
        tk.Entry(prefs_frame, textvariable=self.min_pos_ratio_var, width=6).grid(row=2, column=1, sticky=tk.W)
        tk.Label(prefs_frame, text="Język napisów (obowiązkowy):").grid(row=3, column=0, sticky=tk.W)
        self.sub_lang_var = tk.StringVar(value="")
        sub_combo = ttk.Combobox(prefs_frame, textvariable=self.sub_lang_var,
                                 values=self.all_subtitle_langs, state="readonly", width=15)
        sub_combo.grid(row=3, column=1, sticky=tk.W)
        tk.Label(prefs_frame, text="Platformy:").grid(row=4, column=0, sticky=tk.W)
        self.win_var = tk.BooleanVar(value=True)
        self.mac_var = tk.BooleanVar(value=False)
        self.linux_var = tk.BooleanVar(value=False)
        tk.Checkbutton(prefs_frame, text="Win", variable=self.win_var).grid(row=4, column=1, sticky=tk.W)
        tk.Checkbutton(prefs_frame, text="Mac", variable=self.mac_var).grid(row=4, column=2, sticky=tk.W)
        tk.Checkbutton(prefs_frame, text="Linux", variable=self.linux_var).grid(row=4, column=3, sticky=tk.W)
        weighting_frame = tk.LabelFrame(right_frame, text="Wagi kryteriów")
        weighting_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(weighting_frame, text="Waga pozytywnych recenzji:").grid(row=0, column=0, sticky=tk.W)
        self.scale_pos = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_pos.set(5)
        self.scale_pos.grid(row=0, column=1, sticky=tk.W)
        tk.Label(weighting_frame, text="Waga ceny (ujemna):").grid(row=1, column=0, sticky=tk.W)
        self.scale_price = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_price.set(5)
        self.scale_price.grid(row=1, column=1, sticky=tk.W)
        tk.Label(weighting_frame, text="Pref. język audio:").grid(row=0, column=2, sticky=tk.W)
        self.audio_lang_var = tk.StringVar(value="")
        audio_combo = ttk.Combobox(weighting_frame, textvariable=self.audio_lang_var,
                                   values=self.all_audio_langs, state="readonly", width=15)
        audio_combo.grid(row=0, column=3, sticky=tk.W)
        tk.Label(weighting_frame, text="Waga języka audio:").grid(row=1, column=2, sticky=tk.W)
        self.scale_audio = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_audio.set(0)
        self.scale_audio.grid(row=1, column=3, sticky=tk.W)
        tk.Label(weighting_frame, text="Waga popularności:").grid(row=2, column=0, sticky=tk.W)
        self.scale_owners = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_owners.set(0)
        self.scale_owners.grid(row=2, column=1, sticky=tk.W)
        tk.Label(weighting_frame, text="Waga długości gry:").grid(row=2, column=2, sticky=tk.W)
        self.scale_med = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_med.set(0)
        self.scale_med.grid(row=2, column=3, sticky=tk.W)
        tk.Label(weighting_frame, text="Waga tagów:").grid(row=3, column=0, sticky=tk.W)
        self.scale_tags = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_tags.set(5)
        self.scale_tags.grid(row=3, column=1, sticky=tk.W)
        tags_frame = tk.LabelFrame(right_frame, text="Tagi (wyszukaj i dodaj)")
        tags_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(tags_frame, text="Wyszukaj tag:").grid(row=0, column=0, sticky=tk.W)
        self.tag_search_var = tk.StringVar()
        tk.Entry(tags_frame, textvariable=self.tag_search_var, width=20).grid(row=0, column=1, padx=5, sticky=tk.W)
        self.tag_search_results_list = tk.Listbox(tags_frame, height=5, width=30)
        self.tag_search_results_list.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        tk.Button(tags_frame, text="Szukaj tagów", command=self.search_tags).grid(row=0, column=2, padx=5, sticky=tk.W)
        tk.Button(tags_frame, text="Dodaj tag", command=self.add_selected_tag).grid(row=1, column=2, padx=5, sticky=tk.N)
        tk.Label(tags_frame, text="Wybrane tagi:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.selected_tags_list = tk.Listbox(tags_frame, height=5, width=30)
        self.selected_tags_list.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        tk.Button(tags_frame, text="Usuń tag", command=self.remove_selected_tag).grid(row=3, column=2, padx=5, sticky=tk.N)
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=5)
        recommend_button = tk.Button(button_frame, text="Rekomenduj", command=self.do_recommendation)
        recommend_button.pack(side=tk.LEFT, padx=5)
        self.plot_button = tk.Button(button_frame, text="Pokaż wykres", command=self.show_3d_plot)
        self.plot_button.pack(side=tk.LEFT, padx=5)
        export_button = tk.Button(button_frame, text="Eksportuj do Excela", command=self.export_to_excel)
        export_button.pack(side=tk.LEFT, padx=5)
        columns = ("LP", "Nazwa", "ID", "Wynik", "Cena", "Recenzje", "% Pozytywnych", "Popularność", "Długość gry")
        self.result_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, minwidth=50, width=100, anchor=tk.CENTER)
        self.result_tree.pack(fill=tk.BOTH, expand=True)

    def search_games(self, event=None):
        query = self.search_var.get().strip().lower()
        self.search_results_list.delete(0, tk.END)
        if not query:
            return
        results = []
        for gid, info in self.games_data.items():
            nm = info.get("name", "").lower()
            if query in nm:
                results.append((gid, info.get("name", "")))
        results = results[:100]
        for (gid, name) in results:
            self.search_results_list.insert(tk.END, f"{gid} - {name}")

    def add_to_played(self):
        sel = self.search_results_list.curselection()
        if not sel:
            return
        index = sel[0]
        text_line = self.search_results_list.get(index)
        try:
            gid, name = text_line.split(" - ", 1)
        except:
            return
        if gid not in self.played_game_ids:
            self.played_game_ids.add(gid)
            self.played_games_list.insert(tk.END, f"{gid} - {name}")
        self.search_results_list.delete(index)

    def remove_from_played(self):
        sel = self.played_games_list.curselection()
        if not sel:
            return
        idx = sel[0]
        text_line = self.played_games_list.get(idx)
        try:
            gid = text_line.split(" - ")[0]
        except:
            return
        self.played_game_ids.discard(gid)
        self.played_games_list.delete(idx)

    def show_game_details(self, event):
        source_list = event.widget
        sel = source_list.curselection()
        if not sel:
            return
        index = sel[0]
        text_line = source_list.get(index)
        try:
            gid = text_line.split(" - ", 1)[0].strip()
        except IndexError:
            return
        game_info = self.games_data.get(gid, {})
        if not game_info:
            return
        details_window = tk.Toplevel(self)
        details_window.title(f"Szczegóły gry: {game_info.get('name', 'Unknown')}")
        details_window.geometry("500x400")
        details_text = tk.Text(details_window, wrap=tk.WORD, height=20, width=60)
        details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        details = (
            f"Nazwa: {game_info.get('name', 'Unknown')}\n"
            f"Średni czas gry: {game_info.get('median_playtime_forever', 'Unknown')} minut\n"
            f"Języki audio: {', '.join(game_info.get('full_audio_languages', []))}\n"
            f"Tagi: {', '.join(game_info.get('tags', {}).keys())}\n"
        )
        details_text.insert(tk.END, details)
        details_text.config(state=tk.DISABLED)

    def search_tags(self):
        q = self.tag_search_var.get().strip().lower()
        self.tag_search_results_list.delete(0, tk.END)
        if not q:
            return
        found = []
        for t in self.all_tags:
            if q in t.lower():
                found.append(t)
        found = found[:50]
        for tagg in found:
            self.tag_search_results_list.insert(tk.END, tagg)

    def add_selected_tag(self):
        sel = self.tag_search_results_list.curselection()
        if not sel:
            return
        idx = sel[0]
        chosen = self.tag_search_results_list.get(idx)
        if chosen not in self.selected_tags:
            self.selected_tags.append(chosen)
            self.selected_tags_list.insert(tk.END, chosen)

    def remove_selected_tag(self):
        sel = self.selected_tags_list.curselection()
        if not sel:
            return
        idx = sel[0]
        val = self.selected_tags_list.get(idx)
        self.selected_tags.remove(val)
        self.selected_tags_list.delete(idx)

    def do_recommendation(self):
        method = self.method_var.get()
        max_price = self.max_price_var.get()
        min_rev = self.min_reviews_var.get()
        min_ratio = self.min_pos_ratio_var.get()
        sub_lang = self.sub_lang_var.get().strip()
        platforms = []
        if self.win_var.get():
            platforms.append("windows")
        if self.mac_var.get():
            platforms.append("mac")
        if self.linux_var.get():
            platforms.append("linux")
        w_pos = self.scale_pos.get() / 10.0
        w_price_raw = -(self.scale_price.get() / 10.0)
        w_price = 1 * w_price_raw
        w_audio = self.scale_audio.get() / 10.0
        w_owners = self.scale_owners.get() / 10.0
        w_med = self.scale_med.get() / 10.0
        w_tags = self.scale_tags.get() / 10.0
        pref_audio = self.audio_lang_var.get().strip()
        pref_tags = self.selected_tags[:]
        preferences = {
            "max_price": max_price,
            "min_total_reviews": min_rev,
            "min_positive_ratio": min_ratio,
            "mandatory_sub_lang": sub_lang,
            "required_platforms": platforms,
            "weight_positive_ratio": w_pos,
            "weight_price": w_price,
            "weight_audio_lang": w_audio,
            "weight_owners": w_owners,
            "weight_med_time": w_med,
            "weight_tags": w_tags,
            "preferred_audio_lang": pref_audio,
            "preferred_tags": pref_tags
        }
        played = self.played_game_ids
        if method == "SAW":
            recommended = recommend_games_saw(self.games_data, preferences, top_n=10, played_game_ids=played)
        elif method == "TOPSIS":
            recommended = recommend_games_topsis(self.games_data, preferences, top_n=10, played_game_ids=played)
        elif method == "WPM":
            recommended = recommend_games_wpm(self.games_data, preferences, top_n=10, played_game_ids=played)
        elif method == "VIKOR":
            recommended = recommend_games_vikor(self.games_data, preferences, top_n=10, played_game_ids=played)
        else:
            recommended = []
        for row in self.result_tree.get_children():
            self.result_tree.delete(row)
        self.recommended_games_for_plot.clear()
        if not recommended:
            self.result_tree.insert("", tk.END, values=("Brak", "wyników", "", "", "", "", "", "", ""))
            return
        for i, rec in enumerate(recommended, start=1):
            lp = i
            nm = rec["name"]
            gid = rec["id"]
            sc = rec["score"]
            pr = rec["price"]
            rev = rec["total_reviews"]
            posp = int(rec["pos_percentage"] * 100)
            own = rec.get("estimated_owners", "?")
            med = rec.get("median_playtime_forever", "?")
            self.result_tree.insert("", tk.END, values=(lp, nm, gid, sc, pr, rev, f"{posp}%", own, f"{med} min"))
            self.recommended_games_for_plot.append({
                "name": nm,
                "price": pr,
                "median": med if isinstance(med, (int, float)) else 0,
                "pos_ratio": rec["pos_percentage"],
                "score": sc,
                "owners": own if isinstance(own, (int, float)) else 0
            })

    def export_to_excel(self):
        rows = []
        for child in self.result_tree.get_children():
            row_vals = self.result_tree.item(child)["values"]
            rows.append(row_vals)
        if not rows:
            messagebox.showwarning("Brak wyników", "Brak wyników do wyeksportowania.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Wyniki Rekomendacji"
        headers = ["LP", "Nazwa", "ID", "Wynik", "Cena", "Recenzje", "% Pozytywnych", "Popularność", "Długość gry"]
        sheet.append(headers)
        for row_val in rows:
            sheet.append(list(row_val))
        workbook.save(file_path)
        messagebox.showinfo("Eksport zakończony", f"Wyniki zostały zapisane do pliku: {file_path}")

    def show_3d_plot(self):
        if not self.recommended_games_for_plot:
            return
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x_vals = np.array([g["price"] for g in self.recommended_games_for_plot])
        y_vals = np.array([g["median"] for g in self.recommended_games_for_plot])
        z_vals = np.array([g["pos_ratio"] * 100 for g in self.recommended_games_for_plot])
        c_vals = np.array([g["score"] for g in self.recommended_games_for_plot])
        owners_vals = np.array([g["owners"] for g in self.recommended_games_for_plot])
        s_min, s_max = 75, 500
        o_min, o_max = owners_vals.min(), owners_vals.max() if len(owners_vals) else (0, 0)
        if len(owners_vals) == 0 or o_min == o_max:
            sizes = np.full_like(owners_vals, (s_min + s_max) / 2)
        else:
            sizes = s_min + ((owners_vals - o_min) / (o_max - o_min)) * (s_max - s_min)
        sc = ax.scatter(x_vals, y_vals, z_vals, c=c_vals, cmap="autumn", s=sizes, edgecolors="black")
        ax.set_xlabel("Cena ($)")
        ax.set_ylabel("Mediana czasu gry (min)")
        ax.set_zlabel("Pozytywne recenzje (%)")
        for i, g in enumerate(self.recommended_games_for_plot):
            ax.text(x_vals[i], y_vals[i], z_vals[i], g["name"], size=9)
        plt.colorbar(sc, label="Wynik (score)")
        plt.show()

def extract_zip(zip_path, extract_to):
    print(f"Rozpoczynam wypakowywanie pliku {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Wypakowywanie zakończone. Pliki zostały wypakowane do folderu {extract_to}.")

def main():
    zip_path = "data/games_fixed.zip"
    json_path = "data/games_fixed.json"
    if not os.path.exists(json_path):
        if os.path.exists(zip_path):
            extract_zip(zip_path, "data")
        else:
            print(f"Plik {zip_path} nie istnieje. Sprawdź, czy znajduje się w folderze 'data'.")
            return
    resources_data = load_resources("data/resources.json")
    games_data = load_games(json_path)
    app = GameRecommenderApp(resources_data, games_data)
    app.mainloop()

if __name__ == "__main__":
    main()