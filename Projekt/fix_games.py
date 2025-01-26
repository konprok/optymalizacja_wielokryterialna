import json
from tqdm import tqdm

def load_games(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_games(games_data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(games_data, f, ensure_ascii=False, indent=2)

def fix_games(input_path, output_path):
    games_data = load_games(input_path)
    
    # Lista fraz niepożądanych w tytule
    forbidden_phrases = ["hentai", "porn", "sex", "harem"]
    
    filtered_games = {}
    
    # Zobacz, ile gier mamy w sumie
    total_games = len(games_data)

    # Pętla po grach z paskiem postępu
    # tqdm(games_data.items()) - iterujemy klucz i wartość, jednocześnie widzimy progress
    for game_id, info in tqdm(games_data.items(), desc="Przetwarzanie gier", total=total_games):
        price = info.get("price", 0.0)

        if price == 0:
            continue

        name = info.get("name", "").lower()
        if any(phrase in name for phrase in forbidden_phrases):
            continue

        filtered_games[game_id] = info

    save_games(filtered_games, output_path)
    print(f"Przefiltrowano gry. Zapisano {len(filtered_games)} rekordów do {output_path}")

if __name__ == "__main__":
    fix_games("data/games.json", "data/games_fixed.json")
