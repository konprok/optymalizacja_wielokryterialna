import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from algorithms import topsis, rsm, uta, fuzzy_topsis

def load_data():
    global dane_arkusz1, dane_arkusz2

    file_path = filedialog.askopenfilename(
        title="Wybierz plik",
        filetypes=[("Excel files", "*.xls *.xlsx")]
    )
    if not file_path:
        return

    try:
        dane_arkusz1 = pd.read_excel(file_path, sheet_name=0)
        dane_arkusz2 = pd.read_excel(file_path, sheet_name=1)

        dane_arkusz2["Nr klasy"] = dane_arkusz2["Nr klasy"].astype(int)

        update_table(tabela_alternatywy, dane_arkusz1)
        update_table(tabela_klasy, dane_arkusz2)
        messagebox.showinfo("Sukces", "Dane zostały poprawnie wczytane!")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się wczytać danych: {e}")

def update_table(table, data):
    for row in table.get_children():
        table.delete(row)
    for index, row in data.iterrows():
        table.insert("", "end", values=list(row))

def create_ranking():
    selected_method = metoda_combobox.get()
    if not selected_method:
        messagebox.showwarning("Ostrzeżenie", "Proszę wybrać metodę!")
        return

    try:
        macierz_decyzyjna = dane_arkusz2.iloc[:, 1:4].values
        wagi = np.ones(macierz_decyzyjna.shape[1]) / macierz_decyzyjna.shape[1]

        # Wywołanie wybranego algorytmu
        if selected_method == "TOPSIS":
            ranking, scores = topsis(macierz_decyzyjna, weights=wagi)
        elif selected_method == "RSM":
            ranking, scores = rsm(macierz_decyzyjna, weights=wagi)
        elif selected_method == "UTA":
            utilities, ranking, _ = uta(macierz_decyzyjna, num_segments=5, weights=wagi)
            scores = utilities
        elif selected_method == "Fuzzy TOPSIS":
            fuzzy_matrix = np.expand_dims(macierz_decyzyjna, axis=2)
            fuzzy_matrix = np.concatenate((fuzzy_matrix, fuzzy_matrix, fuzzy_matrix), axis=2)
            fuzzy_weights = [[w, w, w] for w in wagi]
            ranking, scores = fuzzy_topsis(fuzzy_matrix, fuzzy_weights)

        ranking_data = pd.DataFrame({
            "Punkt": [f"({', '.join(map(str, row))})" for row in macierz_decyzyjna],
            "Score": scores
        }).sort_values(by="Score").reset_index(drop=True)

        print("Ranking punktów:")
        print(ranking_data)

        update_table(tabela_ranking, ranking_data)

        create_3d_chart(macierz_decyzyjna, scores, selected_method)

        messagebox.showinfo("Sukces", "Ranking punktów został utworzony!")
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił problem podczas obliczeń: {e}")


def create_3d_chart(macierz_decyzyjna, scores, metoda):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    sc = ax.scatter(
        macierz_decyzyjna[:, 0], macierz_decyzyjna[:, 1], macierz_decyzyjna[:, 2],
        c=scores, cmap="viridis", s=50
    )

    cbar = fig.colorbar(sc, ax=ax, shrink=0.5, aspect=5)
    cbar.set_label("Score")

    ax.set_title(f"Ranking punktów - Wykres 3D\nAlgorytm: {metoda}")
    ax.set_xlabel("Kryterium 1")
    ax.set_ylabel("Kryterium 2")
    ax.set_zlabel("Kryterium 3")

    plt.show()


def create_scrollable_table(frame, columns):
    table = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=25)
    table.pack(fill="both", expand=True)
    return table

root = tk.Tk()
root.title("GUI_OW")
root.geometry("1280x600")

frame_top = tk.Frame(root)
frame_top.pack(pady=10, fill="x")

frame_middle = tk.Frame(root)
frame_middle.pack(pady=10, fill="both", expand=True)

frame_bottom = tk.Frame(root)
frame_bottom.pack(pady=10, fill="both", expand=True)

frame_middle_left = tk.Frame(frame_middle)
frame_middle_left.pack(side=tk.LEFT, fill="both", expand=True)

frame_middle_center = tk.Frame(frame_middle)
frame_middle_center.pack(side=tk.LEFT, fill="both", expand=True)

frame_middle_right = tk.Frame(frame_middle)
frame_middle_right.pack(side=tk.LEFT, fill="both", expand=True)

wczytaj_button = tk.Button(frame_top, text="Wczytaj dane z pliku", command=load_data)
wczytaj_button.pack(side=tk.LEFT, padx=10)

metoda_combobox = ttk.Combobox(frame_top, values=["TOPSIS", "RSM", "UTA", "Fuzzy TOPSIS"], state="readonly")
metoda_combobox.set("Wybierz metodę")
metoda_combobox.pack(side=tk.LEFT, padx=10)

ranking_button = tk.Button(frame_top, text="Stwórz ranking", command=create_ranking)
ranking_button.pack(side=tk.LEFT, padx=10)

tk.Label(frame_middle_left, text="Alternatywy z kryteriami").pack()
tabela_alternatywy = create_scrollable_table(frame_middle_left, ["Nr", "Nazwa", "Kryterium 1", "Kryterium 2", "Kryterium 3"])

tk.Label(frame_middle_center, text="Klasy").pack()
tabela_klasy = create_scrollable_table(frame_middle_center, ["Nr klasy", "x", "y", "z"])

tk.Label(frame_middle_right, text="Stworzony ranking").pack()
tabela_ranking = create_scrollable_table(frame_middle_right, ["Point", "Score"])

dane_arkusz1, dane_arkusz2 = None, None
root.mainloop()