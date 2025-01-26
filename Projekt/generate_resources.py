import json

def load_games(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def gather_unique_data(games_data):
    """
    Zwraca krotkę (set_genres, set_languages) z unikalnymi gatunkami i językami.
    """
    unique_genres = set()
    unique_languages = set()
    unique_audio_languages = set()
    unique_tags = set()

    for game_id, info in games_data.items():
        for g in info.get("genres", []):
            unique_genres.add(g)
            
        for t in info.get("tags", []):
            unique_tags.add(t)
            
        for audio_lang in info.get("full_audio_languages", []):
            unique_audio_languages.add(audio_lang)

        for lang in info.get("supported_languages", []):
            unique_languages.add(lang)

    return unique_genres, unique_languages, unique_audio_languages, unique_tags

def main():
    games_data = load_games("data/games_fixed.json")

    genres_set, languages_set, audio_languages_set, tags_set = gather_unique_data(games_data)

    genres_list = sorted(genres_set)
    languages_list = sorted(languages_set)
    audio_languages = sorted(audio_languages_set)
    tags_list = sorted(tags_set)

    resources = {
        "genres": genres_list,
        "languages": languages_list,
        "audio_languages":  audio_languages,
        "tags": tags_list
    }

    with open("data/resources.json", "w", encoding="utf-8") as f:
        json.dump(resources, f, ensure_ascii=False, indent=2)

    print("Zapisano plik resources.json")

if __name__ == "__main__":
    main()
