import json

def load_games(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_games(games_data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(games_data, f, ensure_ascii=False, indent=2)

def fix_games(input_path, output_path):
    games_data = load_games(input_path)
    
    forbidden_phrases = ["hentai", "porn", "sex", "harem"]
    
    filtered_games = {}

    for game_id, info in games_data.items():
        price = info.get("price", 0.0)
        if price == 0:
            continue

        name_lower = info.get("name", "").lower()
        if any(phrase in name_lower for phrase in forbidden_phrases):
            continue

        filtered_games[game_id] = info

    save_games(filtered_games, output_path)
    print(f"Przefiltrowano gry. Zapisano {len(filtered_games)} rekordów do {output_path}")
    print(f"Liczba gier zapisanych do pliku: {len(filtered_games)}")

if __name__ == "__main__":
    fix_games("data/games.json", "data/games_fixed.json")