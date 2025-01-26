import json
import tkinter as tk
from tkinter import ttk

def load_resources(resources_path):
    with open(resources_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_games(games_path):
    with open(games_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------------------------------------
# FILTRY TWARDE
# --------------------------------------------------------
def game_matches_preferences(game_info, preferences):
    max_price = preferences.get("max_price")
    if max_price is not None:
        if game_info.get("price", 999999) > max_price:
            return False

    min_total_reviews = preferences.get("min_total_reviews", 0)
    pos = game_info.get("positive", 0)
    neg = game_info.get("negative", 0)
    total_reviews = pos + neg
    if total_reviews < min_total_reviews:
        return False

    min_positive_ratio = preferences.get("min_positive_ratio", 0.0)
    ratio = pos / total_reviews if total_reviews > 0 else 0.0
    if ratio < min_positive_ratio:
        return False

    # (Usunięto filtr 'min_metacritic' i sprawdzanie game_info.get("metacritic_score"))

    required_platforms = preferences.get("required_platforms", [])
    for plat in required_platforms:
        if not game_info.get(plat.lower(), False):
            return False

    must_be_multiplayer = preferences.get("must_be_multiplayer", False)
    if must_be_multiplayer:
        categories = game_info.get("categories", [])
        if "Multi-player" not in categories:
            return False

    return True

# --------------------------------------------------------
# SCORING
# --------------------------------------------------------
def compute_game_score(game_info, preferences):
    w_positive_ratio = preferences.get("weight_positive_ratio", 0.0)
    w_price = preferences.get("weight_price", 0.0)
    w_lang = preferences.get("weight_language", 0.0)
    w_tags = preferences.get("weight_tags", 0.0)
    # (Usunięto w_metacritic)

    pos = game_info.get("positive", 0)
    neg = game_info.get("negative", 0)
    total_reviews = pos + neg
    ratio = pos / total_reviews if total_reviews > 0 else 0.0

    price = game_info.get("price", 0.0)

    score = 0.0

    # 1. Procent pozytywnych
    score += w_positive_ratio * ratio
    # 2. Cena (ujemna waga)
    score += w_price * price
    # 3. Język
    preferred_language = preferences.get("preferred_language")
    if preferred_language:
        supported_langs = game_info.get("supported_languages", [])
        if preferred_language in supported_langs:
            score += w_lang
    # 4. Tagi
    preferred_tags = preferences.get("preferred_tags", [])
    if preferred_tags:
        game_tags = game_info.get("tags", [])
        matched_tags = sum(1 for t in preferred_tags if t in game_tags)
        fraction_tags = matched_tags / len(preferred_tags)
        score += fraction_tags * w_tags

    return score

def recommend_games(games_data, preferences, exclude_ids=None, top_n=10):
    if exclude_ids is None:
        exclude_ids = set()

    filtered = []
    for game_id, info in games_data.items():
        if game_id in exclude_ids:
            continue
        if game_matches_preferences(info, preferences):
            filtered.append((game_id, info))

    scored = []
    for game_id, info in filtered:
        sc = compute_game_score(info, preferences)
        scored.append((game_id, sc))

    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[:top_n]

    results = []
    for game_id, sc in best:
        info = games_data[game_id]
        pos = info.get("positive", 0)
        neg = info.get("negative", 0)
        total_rev = pos + neg
        ratio = round(pos / total_rev, 2) if total_rev > 0 else 0.0

        results.append({
            "id": game_id,
            "name": info.get("name", ""),
            "score": round(sc, 2),
            "price": info.get("price", 0),
            "pos_percentage": ratio,
            "total_reviews": total_rev
        })
    return results

# --------------------------------------------------------
# GUI - skale 0..10
# --------------------------------------------------------
class GameRecommenderApp(tk.Tk):
    def __init__(self, resources_data, games_data):
        super().__init__()
        self.title("Game Recommender (Scale 0–10, 0 = pominięcie kryterium)")
        self.geometry("1200x800")

        self.all_languages = resources_data["languages"]
        self.all_tags = resources_data["tags"]

        self.games_data = games_data
        self.played_game_ids = set()
        self.selected_tags = []

        self.build_gui()

    def build_gui(self):
        left_frame = tk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # -----------------------------
        # LEWA RAMKA - wyszukiwarka
        # -----------------------------
        tk.Label(left_frame, text="Wyszukaj grę po nazwie:").pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(left_frame, textvariable=self.search_var, width=30)
        search_entry.pack(fill=tk.X, pady=5)

        search_button = tk.Button(left_frame, text="Szukaj", command=self.search_games)
        search_button.pack(pady=5)

        self.search_results_list = tk.Listbox(left_frame, height=15, width=50)
        self.search_results_list.pack(fill=tk.BOTH, expand=True)

        add_played_button = tk.Button(left_frame, text="Dodaj do ogranych", command=self.add_to_played)
        add_played_button.pack(pady=5)

        # -----------------------------
        # PRAWA RAMKA - filtry + wagi
        # -----------------------------
        prefs_frame = tk.LabelFrame(right_frame, text="Filtry twarde")
        prefs_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(prefs_frame, text="Maks. cena:").grid(row=0, column=0, sticky=tk.W)
        self.max_price_var = tk.DoubleVar(value=30.0)
        tk.Entry(prefs_frame, textvariable=self.max_price_var, width=6).grid(row=0, column=1, sticky=tk.W)

        tk.Label(prefs_frame, text="Min. liczba recenzji:").grid(row=1, column=0, sticky=tk.W)
        self.min_reviews_var = tk.IntVar(value=10)
        tk.Entry(prefs_frame, textvariable=self.min_reviews_var, width=6).grid(row=1, column=1, sticky=tk.W)

        tk.Label(prefs_frame, text="Min. % pozytywnych (0..1):").grid(row=2, column=0, sticky=tk.W)
        self.min_pos_ratio_var = tk.DoubleVar(value=0.5)
        tk.Entry(prefs_frame, textvariable=self.min_pos_ratio_var, width=6).grid(row=2, column=1, sticky=tk.W)

        # (Usunięto sekcję 'Min. Metacritic')

        tk.Label(prefs_frame, text="Platformy:").grid(row=3, column=0, sticky=tk.W)
        self.win_var = tk.BooleanVar(value=True)
        self.mac_var = tk.BooleanVar(value=False)
        self.linux_var = tk.BooleanVar(value=False)
        tk.Checkbutton(prefs_frame, text="Win", variable=self.win_var).grid(row=3, column=1, sticky=tk.W)
        tk.Checkbutton(prefs_frame, text="Mac", variable=self.mac_var).grid(row=3, column=2, sticky=tk.W)
        tk.Checkbutton(prefs_frame, text="Linux", variable=self.linux_var).grid(row=3, column=3, sticky=tk.W)

        self.mp_var = tk.BooleanVar(value=False)
        tk.Checkbutton(prefs_frame, text="Wymag. Multiplayer", variable=self.mp_var)\
            .grid(row=4, column=0, columnspan=2, sticky=tk.W)

        weighting_frame = tk.LabelFrame(right_frame, text="Preferencje miękkie (skala 0–10, 0 = pomiń kryterium)")
        weighting_frame.pack(fill=tk.X, padx=5, pady=5)

        # 1. Waga % pozytywnych
        tk.Label(weighting_frame, text="Waga % pozyt. [0–10]:").grid(row=0, column=0, sticky=tk.W)
        self.scale_pos_ratio = tk.Scale(weighting_frame, from_=0, to=10, orient=tk.HORIZONTAL, resolution=1)
        self.scale_pos_ratio.set(5)  # domyślna wartość
        self.scale_pos_ratio.grid(row=0, column=1, sticky=tk.W)

        # 2. Waga ceny (ujemna)
        tk.Label(weighting_frame, text="Waga ceny [0–10, ujemna]:").grid(row=1, column=0, sticky=tk.W)
        self.scale_price = tk.Scale(weighting_frame, from_=0, to=10, orient=tk.HORIZONTAL, resolution=1)
        self.scale_price.set(5)
        self.scale_price.grid(row=1, column=1, sticky=tk.W)

        # 3. Waga języka
        tk.Label(weighting_frame, text="Waga języka [0–10]:").grid(row=1, column=2, sticky=tk.W)
        self.scale_language = tk.Scale(weighting_frame, from_=0, to=10, orient=tk.HORIZONTAL, resolution=1)
        self.scale_language.set(5)
        self.scale_language.grid(row=1, column=3, sticky=tk.W)

        tk.Label(weighting_frame, text="Preferowany język:").grid(row=2, column=0, sticky=tk.W)
        self.language_var = tk.StringVar(value="English")
        self.language_combo = ttk.Combobox(weighting_frame, textvariable=self.language_var,
                                           values=self.all_languages, state="readonly", width=15)
        self.language_combo.grid(row=2, column=1, sticky=tk.W)

        # 4. Waga tagów
        tk.Label(weighting_frame, text="Waga tagów [0–10]:").grid(row=2, column=2, sticky=tk.W)
        self.scale_tags = tk.Scale(weighting_frame, from_=0, to=10, orient=tk.HORIZONTAL, resolution=1)
        self.scale_tags.set(5)
        self.scale_tags.grid(row=2, column=3, sticky=tk.W)

        # Wyszukiwarka tagów
        tags_frame = tk.LabelFrame(right_frame, text="Tagi (wyszukaj i dodaj do wybranych)")
        tags_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(tags_frame, text="Wyszukaj tag:").grid(row=0, column=0, sticky=tk.W)
        self.tag_search_var = tk.StringVar()
        tag_search_entry = tk.Entry(tags_frame, textvariable=self.tag_search_var, width=20)
        tag_search_entry.grid(row=0, column=1, padx=5, sticky=tk.W)

        self.tag_search_results_list = tk.Listbox(tags_frame, height=5, width=30)
        self.tag_search_results_list.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        tag_search_button = tk.Button(tags_frame, text="Szukaj tagów", command=self.search_tags)
        tag_search_button.grid(row=0, column=2, padx=5, sticky=tk.W)

        add_tag_button = tk.Button(tags_frame, text="Dodaj tag do wybranych", command=self.add_selected_tag)
        add_tag_button.grid(row=1, column=2, padx=5, sticky=tk.N)

        tk.Label(tags_frame, text="Wybrane tagi:").grid(row=2, column=0, sticky=tk.W, pady=(10,0))
        self.selected_tags_list = tk.Listbox(tags_frame, height=5, width=30)
        self.selected_tags_list.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        remove_tag_button = tk.Button(tags_frame, text="Usuń zaznaczony tag", command=self.remove_selected_tag)
        remove_tag_button.grid(row=3, column=2, padx=5, sticky=tk.N)

        recommend_button = tk.Button(right_frame, text="Rekomenduj", command=self.do_recommendation)
        recommend_button.pack(pady=5)

        self.result_text = tk.Text(right_frame, height=15, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    # --------------------------------------------------------
    # FUNKCJE OBSŁUGI GIER
    # --------------------------------------------------------
    def search_games(self):
        query = self.search_var.get().strip().lower()
        self.search_results_list.delete(0, tk.END)
        if not query:
            return

        results = []
        for game_id, info in self.games_data.items():
            name = info.get("name", "").lower()
            if query in name:
                results.append((game_id, info.get("name", "")))

        results = results[:100]
        for game_id, game_name in results:
            self.search_results_list.insert(tk.END, f"{game_id} - {game_name}")

    def add_to_played(self):
        sel = self.search_results_list.curselection()
        if not sel:
            return
        index = sel[0]
        text_line = self.search_results_list.get(index)
        game_id = text_line.split(" - ", 1)[0]
        self.played_game_ids.add(game_id)
        self.search_results_list.delete(index)

    # --------------------------------------------------------
    # FUNKCJE OBSŁUGI TAGÓW
    # --------------------------------------------------------
    def search_tags(self):
        query = self.tag_search_var.get().strip().lower()
        self.tag_search_results_list.delete(0, tk.END)
        if not query:
            return

        found_tags = []
        for t in self.all_tags:
            if query in t.lower():
                found_tags.append(t)

        found_tags = found_tags[:50]
        for t in found_tags:
            self.tag_search_results_list.insert(tk.END, t)

    def add_selected_tag(self):
        sel = self.tag_search_results_list.curselection()
        if not sel:
            return
        index = sel[0]
        chosen_tag = self.tag_search_results_list.get(index)

        if chosen_tag not in self.selected_tags:
            self.selected_tags.append(chosen_tag)
            self.selected_tags_list.insert(tk.END, chosen_tag)

    def remove_selected_tag(self):
        sel = self.selected_tags_list.curselection()
        if not sel:
            return
        index = sel[0]
        tag_to_remove = self.selected_tags_list.get(index)
        self.selected_tags.remove(tag_to_remove)
        self.selected_tags_list.delete(index)

    # --------------------------------------------------------
    # GENEROWANIE REKOMENDACJI
    # --------------------------------------------------------
    def do_recommendation(self):
        # --- Filtry twarde ---
        max_price = self.max_price_var.get()
        min_total_reviews = self.min_reviews_var.get()
        min_positive_ratio = self.min_pos_ratio_var.get()
        # usunęliśmy min_metacritic - już go nie czytamy
        # self.min_metacritic_var = ?

        required_platforms = []
        if self.win_var.get():
            required_platforms.append("windows")
        if self.mac_var.get():
            required_platforms.append("mac")
        if self.linux_var.get():
            required_platforms.append("linux")

        must_be_multiplayer = self.mp_var.get()

        # --- Wagi z suwnic 0..10 => (wartość / 10.0)
        w_positive_ratio = self.scale_pos_ratio.get() / 10.0
        w_price = -(self.scale_price.get() / 10.0)
        w_language = self.scale_language.get() / 10.0
        w_tags = self.scale_tags.get() / 10.0

        preferred_language = self.language_var.get().strip()
        preferred_tags = self.selected_tags[:]

        preferences = {
            # Filtry twarde
            "max_price": max_price,
            "min_total_reviews": min_total_reviews,
            "min_positive_ratio": min_positive_ratio,
            # usunięto "min_metacritic"
            "required_platforms": required_platforms,
            "must_be_multiplayer": must_be_multiplayer,

            # Preferencje miękkie
            "preferred_language": preferred_language,
            "preferred_tags": preferred_tags,

            # Wagi
            "weight_positive_ratio": w_positive_ratio,
            "weight_price": w_price,
            "weight_language": w_language,
            "weight_tags": w_tags
        }

        recommended = recommend_games(
            self.games_data,
            preferences,
            exclude_ids=self.played_game_ids,
            top_n=10
        )

        self.result_text.delete("1.0", tk.END)
        if not recommended:
            self.result_text.insert(tk.END, "Brak wyników.\n")
            return

        for i, rec in enumerate(recommended, start=1):
            line = (
                f"{i}. {rec['name']} (ID: {rec['id']})\n"
                f"   Score: {rec['score']}, Price: {rec['price']}, "
                f"Liczba recenzji: {rec['total_reviews']}, "
                f"% pozytywnych: {int(rec['pos_percentage']*100)}%\n\n"
            )
            self.result_text.insert(tk.END, line)

def main():
    resources_data = load_resources("data/resources.json")
    games_data = load_games("data/games_fixed.json")
    app = GameRecommenderApp(resources_data, games_data)
    app.mainloop()

if __name__ == "__main__":
    main()
