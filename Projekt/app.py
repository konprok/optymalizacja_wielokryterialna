import json
import tkinter as tk
from tkinter import ttk
import math

def load_resources(resources_path):
    with open(resources_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_games(games_path):
    with open(games_path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------
# POMOCNICZE FUNKCJE PARSUJĄCE
# -----------------------

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
                low = int(parts[0].strip().replace(",",""))
                high = int(parts[1].strip().replace(",",""))
                return (low + high)//2
            except:
                return 0
    else:
        try:
            return int(val.replace(",",""))
        except:
            return 0
    return 0

def parse_price(price_value):
    if isinstance(price_value, (int,float)):
        return float(price_value)
    if isinstance(price_value, str):
        try:
            return float(price_value)
        except:
            return 0.0
    return 0.0

# -----------------------
# FILTRY TWARDE
# -----------------------
def game_matches_preferences(game_info, preferences):
    # 1. Maksymalna cena
    max_price = preferences.get("max_price")
    if max_price is not None:
        price_val = parse_price(game_info.get("price", 999999))
        if price_val > max_price:
            return False

    # 2. Min. liczba recenzji
    min_total_reviews = preferences.get("min_total_reviews", 0)
    pos = game_info.get("positive", 0)
    neg = game_info.get("negative", 0)
    total_reviews = pos + neg
    if total_reviews < min_total_reviews:
        return False

    # 3. Min. % pozytywnych
    min_positive_ratio = preferences.get("min_positive_ratio", 0.0)
    ratio = pos / total_reviews if total_reviews > 0 else 0.0
    if ratio < min_positive_ratio:
        return False

    # 4. Obowiązkowy język napisów
    mand_sub = preferences.get("mandatory_sub_lang", "")
    if mand_sub:
        supp_langs = game_info.get("supported_languages", [])
        if mand_sub not in supp_langs:
            return False

    # 5. Wymagane platformy
    req_plat = preferences.get("required_platforms", [])
    for rp in req_plat:
        if not game_info.get(rp.lower(), False):
            return False

    return True

# -----------------------
# SAW
# -----------------------
def compute_score_saw(game_info, preferences):
    w_positive_ratio = preferences.get("weight_positive_ratio", 0.0)
    w_price = preferences.get("weight_price", 0.0)
    w_audio = preferences.get("weight_audio_lang", 0.0)
    w_owners = preferences.get("weight_owners", 0.0)
    w_avg = preferences.get("weight_avg_time", 0.0)
    w_med = preferences.get("weight_med_time", 0.0)
    w_tags = preferences.get("weight_tags", 0.0)

    pos = game_info.get("positive", 0)
    neg = game_info.get("negative", 0)
    total_reviews = pos + neg
    ratio = pos/total_reviews if total_reviews>0 else 0.0

    # Cena
    price = parse_price(game_info.get("price", 0.0))
    # Zmniejszenie wpływu ceny przez czynnik 0.5
    w_price_adjusted = 0.1 * w_price

    # Preferowany język audio
    full_audio = game_info.get("full_audio_languages", [])
    pref_audio = preferences.get("preferred_audio_lang", "")

    # owners
    owners_str = game_info.get("estimated_owners", "0")
    owners = parse_owners(owners_str)

    # Czasy
    avg_time = game_info.get("average_playtime_forever", 0)
    med_time = game_info.get("median_playtime_forever", 0)

    # Tagi
    game_tags = game_info.get("tags", {})
    pref_tags = preferences.get("preferred_tags", [])

    score = 0.0

    # 1. % pozytywnych (benefit)
    score += w_positive_ratio * ratio

    # 2. Cena (cost)
    score += w_price_adjusted * price

    # 3. Preferowany język audio
    if pref_audio and pref_audio in full_audio:
        score += w_audio

    # 4. owners
    owners_norm = math.log(owners+1,10) if owners>0 else 0
    score += w_owners * owners_norm

    # 5. avg_time
    max_min = 6000.0
    avg_norm = avg_time / max_min if avg_time<max_min else 1.0
    score += w_avg * avg_norm

    # 6. med_time
    med_norm = med_time / max_min if med_time<max_min else 1.0
    score += w_med * med_norm

    # 7. Tagi
    if pref_tags:
        matched = sum(1 for t in pref_tags if t in game_tags)
        frac = matched/len(pref_tags)
        score += w_tags * frac

    return score

def recommend_games_saw(games_data, preferences, top_n=10):
    filtered = []
    for gid, info in games_data.items():
        if game_matches_preferences(info, preferences):
            filtered.append((gid, info))

    scored = []
    for (gid, info) in filtered:
        sc = compute_score_saw(info, preferences)
        scored.append((gid, sc))

    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[:top_n]

    results = []
    for (gid, sc) in best:
        info = games_data[gid]
        p = parse_price(info.get("price",0))
        pos = info.get("positive",0)
        neg = info.get("negative",0)
        tot = pos+neg
        ratio = round(pos/tot,2) if tot>0 else 0.0
        results.append({
            "id": gid,
            "name": info.get("name",""),
            "score": round(sc,2),
            "price": p,
            "pos_percentage": ratio,
            "total_reviews": tot,
            "required_age": info.get("required_age",0),
            "estimated_owners": parse_owners(info.get("estimated_owners","0")),
            "average_playtime_forever": info.get("average_playtime_forever",0),
            "median_playtime_forever": info.get("median_playtime_forever",0),
        })
    return results

# -----------------------
# TOPSIS
# -----------------------
def recommend_games_topsis(games_data, preferences, top_n=10):
    candidate_games = []
    for gid, info in games_data.items():
        if game_matches_preferences(info, preferences):
            candidate_games.append((gid, info))

    if not candidate_games:
        return []

    w_pos = preferences.get("weight_positive_ratio", 0.0)
    w_price_raw = abs(preferences.get("weight_price", 0.0))
    # Zmniejszamy siłę ceny x0.5
    w_price = 0.1 * w_price_raw
    w_owners = preferences.get("weight_owners", 0.0)
    w_avg = preferences.get("weight_avg_time", 0.0)

    sum_w = w_pos + w_price + w_owners + w_avg
    if sum_w < 1e-9:
        sum_w = 1.0

    game_ids = []
    data_matrix = []
    for (gid, info) in candidate_games:
        pos = info.get("positive",0)
        neg = info.get("negative",0)
        tot = pos+neg
        ratio = pos/tot if tot>0 else 0.0

        price = parse_price(info.get("price",0))
        owners = parse_owners(info.get("estimated_owners","0"))
        avg_time = info.get("average_playtime_forever",0)

        row = [ ratio, price, owners, avg_time ]
        data_matrix.append(row)
        game_ids.append(gid)

    w_array = [
        w_pos/sum_w,
        w_price/sum_w,
        w_owners/sum_w,
        w_avg/sum_w
    ]
    # 0=pos(b),1=price(c),2=owners(b),3=avg(b)
    cost_benefit = [False, True, False, False]

    rows = len(data_matrix)
    if rows == 0:
        return []
    cols = 4

    col_sumsq = [0.0]*cols
    for r in range(rows):
        for c in range(cols):
            val = float(data_matrix[r][c])
            col_sumsq[c] += val*val

    # Normalizacja
    for r in range(rows):
        for c in range(cols):
            if col_sumsq[c] > 0:
                data_matrix[r][c] /= math.sqrt(col_sumsq[c])
            else:
                data_matrix[r][c] = 0.0

    # Mnożenie przez wagi
    for r in range(rows):
        for c in range(cols):
            data_matrix[r][c] *= w_array[c]

    # Ideał / antyideał
    ideal = [0.0]*cols
    anti_ideal = [0.0]*cols
    for c in range(cols):
        column_vals = [data_matrix[r][c] for r in range(rows)]
        if cost_benefit[c] == False:
            # benefit
            ideal[c] = max(column_vals)
            anti_ideal[c] = min(column_vals)
        else:
            # cost
            ideal[c] = min(column_vals)
            anti_ideal[c] = max(column_vals)

    # Odległości
    distances = []
    for r in range(rows):
        dist_plus = 0.0
        dist_minus = 0.0
        for c in range(cols):
            dist_plus += (data_matrix[r][c] - ideal[c])**2
            dist_minus += (data_matrix[r][c] - anti_ideal[c])**2
        dist_plus = math.sqrt(dist_plus)
        dist_minus = math.sqrt(dist_minus)
        ci = dist_minus/(dist_plus+dist_minus) if (dist_plus+dist_minus)>0 else 0.0
        distances.append(ci)

    combined = list(zip(game_ids, distances))
    combined.sort(key=lambda x: x[1], reverse=True)
    best = combined[:top_n]

    results = []
    for (gid, ci) in best:
        info = games_data[gid]
        pos = info.get("positive",0)
        neg = info.get("negative",0)
        tot = pos+neg
        ratio = round(pos/tot,2) if tot>0 else 0.0
        p = parse_price(info.get("price",0))
        results.append({
            "id": gid,
            "name": info.get("name",""),
            "score": round(ci,2),
            "price": p,
            "pos_percentage": ratio,
            "total_reviews": tot,
            "required_age": info.get("required_age",0),
            "estimated_owners": parse_owners(info.get("estimated_owners","0")),
            "average_playtime_forever": info.get("average_playtime_forever",0),
            "median_playtime_forever": info.get("median_playtime_forever",0),
        })
    return results

class GameRecommenderApp(tk.Tk):
    def __init__(self, resources_data, games_data):
        super().__init__()
        self.title("Game Recommender – SAW vs TOPSIS (bez daty, usunięto 'darmowe')")
        self.geometry("1200x800")

        # resource
        self.all_subtitle_langs = resources_data["languages"]         
        self.all_audio_langs = resources_data["audio_languages"]     
        self.all_tags = resources_data["tags"]
        self.games_data = games_data

        self.selected_tags = []

        self.build_gui()

    def build_gui(self):
        # Lewy panel - wyszukiwarka
        left_frame = tk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        tk.Label(left_frame, text="Wyszukaj grę po nazwie:").pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.search_var, width=30).pack(fill=tk.X, pady=5)
        tk.Button(left_frame, text="Szukaj", command=self.search_games).pack(pady=5)

        self.search_results_list = tk.Listbox(left_frame, height=15, width=50)
        self.search_results_list.pack(fill=tk.BOTH, expand=True)

        # Prawy panel
        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Metoda
        method_frame = tk.LabelFrame(right_frame, text="Metoda wielokryterialna")
        method_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(method_frame, text="Wybierz metodę:").grid(row=0, column=0, sticky=tk.W)
        self.method_var = tk.StringVar(value="SAW")
        self.method_combo = ttk.Combobox(method_frame, textvariable=self.method_var,
                                         values=["SAW","TOPSIS"],
                                         state="readonly", width=15)
        self.method_combo.grid(row=0, column=1, sticky=tk.W)

        # Filtry twarde
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

        tk.Label(prefs_frame, text="Obowiązkowy język napisów:").grid(row=3, column=0, sticky=tk.W)
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

        # Kryteria
        weighting_frame = tk.LabelFrame(right_frame, text="Kryteria (0..10)")
        weighting_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(weighting_frame, text="Waga % pozyt.:").grid(row=0, column=0, sticky=tk.W)
        self.scale_pos_ratio = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_pos_ratio.set(5)
        self.scale_pos_ratio.grid(row=0, column=1, sticky=tk.W)

        tk.Label(weighting_frame, text="Waga ceny (ujemna):").grid(row=1, column=0, sticky=tk.W)
        self.scale_price = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_price.set(5)
        self.scale_price.grid(row=1, column=1, sticky=tk.W)

        tk.Label(weighting_frame, text="Pref. język aduio:").grid(row=0, column=2, sticky=tk.W)
        self.audio_lang_var = tk.StringVar(value="")
        audio_combo = ttk.Combobox(weighting_frame, textvariable=self.audio_lang_var,
                                   values=self.all_audio_langs, state="readonly", width=12)
        audio_combo.grid(row=0, column=3, sticky=tk.W)

        tk.Label(weighting_frame, text="Waga język audio:").grid(row=1, column=2, sticky=tk.W)
        self.scale_audio_lang = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_audio_lang.set(0)
        self.scale_audio_lang.grid(row=1, column=3, sticky=tk.W)

        tk.Label(weighting_frame, text="Waga popularności:").grid(row=2, column=0, sticky=tk.W)
        self.scale_owners = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_owners.set(0)
        self.scale_owners.grid(row=2, column=1, sticky=tk.W)

        tk.Label(weighting_frame, text="Waga średniego czasu rozgrywki:").grid(row=2, column=2, sticky=tk.W)
        self.scale_avgtime = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_avgtime.set(0)
        self.scale_avgtime.grid(row=2, column=3, sticky=tk.W)

        tk.Label(weighting_frame, text="Waga mediany czasu rozgrywki:").grid(row=3, column=2, sticky=tk.W)
        self.scale_medtime = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_medtime.set(0)
        self.scale_medtime.grid(row=3, column=3, sticky=tk.W)

        tk.Label(weighting_frame, text="Waga tagów:").grid(row=3, column=0, sticky=tk.W)
        self.scale_tags = tk.Scale(weighting_frame, from_=0, to=10, resolution=1, orient=tk.HORIZONTAL)
        self.scale_tags.set(5)
        self.scale_tags.grid(row=3, column=1, sticky=tk.W)

        # Tagi
        tags_frame = tk.LabelFrame(right_frame, text="Tagi (wyszukaj i dodaj do wybranych)")
        tags_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(tags_frame, text="Wyszukaj tag:").grid(row=0, column=0, sticky=tk.W)
        self.tag_search_var = tk.StringVar()
        tk.Entry(tags_frame, textvariable=self.tag_search_var, width=20).grid(row=0, column=1, padx=5, sticky=tk.W)

        self.tag_search_results_list = tk.Listbox(tags_frame, height=5, width=30)
        self.tag_search_results_list.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        tk.Button(tags_frame, text="Szukaj tagów", command=self.search_tags).grid(row=0, column=2, padx=5, sticky=tk.W)
        tk.Button(tags_frame, text="Dodaj tag do wybranych", command=self.add_selected_tag)\
            .grid(row=1, column=2, padx=5, sticky=tk.N)

        tk.Label(tags_frame, text="Wybrane tagi:").grid(row=2, column=0, sticky=tk.W, pady=(10,0))
        self.selected_tags_list = tk.Listbox(tags_frame, height=5, width=30)
        self.selected_tags_list.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        tk.Button(tags_frame, text="Usuń zaznaczony tag", command=self.remove_selected_tag)\
            .grid(row=3, column=2, padx=5, sticky=tk.N)

        recommend_button = tk.Button(right_frame, text="Rekomenduj", command=self.do_recommendation)
        recommend_button.pack(pady=5)

        self.result_text = tk.Text(right_frame, height=15, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def search_games(self):
        query = self.search_var.get().strip().lower()
        self.search_results_list.delete(0, tk.END)
        if not query:
            return
        results = []
        for gid, info in self.games_data.items():
            nm = info.get("name","").lower()
            if query in nm:
                results.append((gid, info.get("name","")))

        results = results[:100]
        for (gid, gname) in results:
            self.search_results_list.insert(tk.END, f"{gid} - {gname}")

    def search_tags(self):
        query = self.tag_search_var.get().strip().lower()
        self.tag_search_results_list.delete(0, tk.END)
        if not query:
            return
        found = []
        for t in self.all_tags:
            if query in t.lower():
                found.append(t)
        found = found[:50]
        for fz in found:
            self.tag_search_results_list.insert(tk.END, fz)

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
        tg = self.selected_tags_list.get(idx)
        self.selected_tags.remove(tg)
        self.selected_tags_list.delete(idx)

    def do_recommendation(self):
        method = self.method_var.get()

        # Filtry twarde
        max_price = self.max_price_var.get()
        min_reviews = self.min_reviews_var.get()
        min_ratio = self.min_pos_ratio_var.get()
        mand_sub = self.sub_lang_var.get().strip()

        platforms = []
        if self.win_var.get():
            platforms.append("windows")
        if self.mac_var.get():
            platforms.append("mac")
        if self.linux_var.get():
            platforms.append("linux")

        # Wagi
        w_pos = self.scale_pos_ratio.get()/10.0
        # łagodzimy cenę
        w_price_raw = -(self.scale_price.get()/10.0)
        w_price = 0.5 * w_price_raw

        w_audio = self.scale_audio_lang.get()/10.0
        w_owners = self.scale_owners.get()/10.0
        w_avg = self.scale_avgtime.get()/10.0
        w_med = self.scale_medtime.get()/10.0
        w_tags = self.scale_tags.get()/10.0

        pref_audio = self.audio_lang_var.get().strip()
        pref_tags = self.selected_tags[:]

        preferences = {
            "max_price": max_price,
            "min_total_reviews": min_reviews,
            "min_positive_ratio": min_ratio,
            "mandatory_sub_lang": mand_sub,
            "required_platforms": platforms,

            "weight_positive_ratio": w_pos,
            "weight_price": w_price,
            "weight_audio_lang": w_audio,
            "weight_owners": w_owners,
            "weight_avg_time": w_avg,
            "weight_med_time": w_med,
            "weight_tags": w_tags,

            "preferred_audio_lang": pref_audio,
            "preferred_tags": pref_tags
        }

        if method=="SAW":
            recommended = recommend_games_saw(self.games_data, preferences, top_n=10)
        elif method=="TOPSIS":
            recommended = recommend_games_topsis(self.games_data, preferences, top_n=10)
        else:
            recommended = []

        self.result_text.delete("1.0", tk.END)
        if not recommended:
            self.result_text.insert(tk.END, "Brak wyników.\n")
            return

        for i, rec in enumerate(recommended, start=1):
            line = (
                f"{i}. {rec['name']} (ID: {rec['id']})\n"
                f"   Score: {rec['score']}, Price: {rec['price']}, "
                f"Reviews: {rec['total_reviews']}, "
                f"% Positive: {int(rec['pos_percentage']*100)}%, "
                f"Owners: {rec.get('estimated_owners','?')}, "
                f"Avg: {rec.get('average_playtime_forever','?')}min, "
                f"Med: {rec.get('median_playtime_forever','?')}min\n\n"
            )
            self.result_text.insert(tk.END, line)


def main():
    resources_data = load_resources("data/resources.json")
    games_data = load_games("data/games_fixed.json")
    app = GameRecommenderApp(resources_data, games_data)
    app.mainloop()

if __name__=="__main__":
    main()