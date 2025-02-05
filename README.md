# Optymalizacja Wielokryterialna

## Opis projektu

To repozytorium zawiera materiały i implementacje związane z tematyką optymalizacji wielokryterialnej, opracowane w ramach zajęć akademickich. Celem jest analiza i rozwiązywanie problemów decyzyjnych z wieloma kryteriami oceny.

## Projekt końcowy

# System rekomendacji gier wideo

Projekt ma na celu stworzenie systemu wspomagania decyzji, który wspiera użytkowników w wyborze gier wideo na podstawie określonych preferencji. Problem wyboru gry został ujęty jako zadanie optymalizacji wielokryterialnej, gdzie uwzględniane są różne czynniki wpływające na decyzję, takie jak:

- **Cena gry**
- **Liczba ocen i % pozytywnych recenzji użytkowników**
- **Gatunki, kategorie i tagi**
- **Obsługiwane języki - napisy oraz dubbing**
- **Dostępność na różnych platformach (Windows, Mac, Linux)**

Dane do systemu rekomendacji pochodzą z [Steam Web API](https://steamcommunity.com/dev).

## Źródło danych

Aplikacja korzysta z pliku **`games_fixed.json`**, który zawiera informacje o grach pobranych z platformy Steam, po wstępnym oczyszczeniu i filtracji. Dane zawierają:

- **Nazwę gry**
- **Datę wydania**
- **Cenę**
- **Opis gry**
- **Recenzje użytkowników**
- **Obsługiwane platformy**
- **Liczbę rekomendacji i ocen**
- **Kategorie, gatunki oraz tagi**

Przykładowy wpis:

```json
{
  "20200": {
    "name": "Galactic Bowling",
    "release_date": "Oct 21, 2008",
    "price": 19.99,
    "categories": ["Single-player", "Multi-player"],
    "genres": ["Casual", "Indie", "Sports"],
    "positive": 6,
    "negative": 11,
    "tags": {"Indie": 22, "Casual": 21, "Sports": 21}
  }
}

```

# Rozwiazanie

W projekcie zaimplementowano cztery metody wielokryterialne, które następnie porównano w celu ustalenia ich efektywności w kontekście rekomendacji gier:

- **SAW (Simple Additive Weighting)**
- **WPM (Weighted Product Method)**
- **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)****
- **VIKOR (VIseKriterijumska Optimizacija kompromisno Resenje)**

Każda z tych metod analizuje wielokryterialne dane wejściowe i oblicza najbardziej optymalne rekomendacje, czyli listę 10 najlepiej dopsowanych gier dla użytkownika.
