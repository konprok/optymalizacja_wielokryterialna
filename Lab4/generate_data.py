import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from scipy.stats import norm, expon


class OptimizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generowanie Punktów i Alternatyw")

        self.samples = np.array([])
        self.alternatives = []

        self.alternative_frame = ttk.LabelFrame(root, text="Dodawanie Alternatyw")
        self.alternative_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(self.alternative_frame, text="Kryterium 1:").grid(row=0, column=0, padx=5, pady=5)
        self.crit1_entry = tk.Entry(self.alternative_frame)
        self.crit1_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.alternative_frame, text="Kryterium 2:").grid(row=1, column=0, padx=5, pady=5)
        self.crit2_entry = tk.Entry(self.alternative_frame)
        self.crit2_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.alternative_frame, text="Kryterium 3:").grid(row=2, column=0, padx=5, pady=5)
        self.crit3_entry = tk.Entry(self.alternative_frame)
        self.crit3_entry.grid(row=2, column=1, padx=5, pady=5)

        self.add_alternative_button = tk.Button(self.alternative_frame, text="Dodaj Alternatywę", command=self.add_alternative)
        self.add_alternative_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.alt_table_frame = ttk.LabelFrame(root, text="Alternatywy")
        self.alt_table_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.alt_table = ttk.Treeview(self.alt_table_frame, columns=["Nr", "Nazwa", "Kryterium 1", "Kryterium 2", "Kryterium 3"], show="headings")
        for col in ["Nr", "Nazwa", "Kryterium 1", "Kryterium 2", "Kryterium 3"]:
            self.alt_table.heading(col, text=col)
            self.alt_table.column(col, width=100)
        self.alt_table.grid(row=0, column=0, padx=5, pady=5)

        self.generation_frame = ttk.LabelFrame(root, text="Generacja Punktów")
        self.generation_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(self.generation_frame, text="Rozkład:").grid(row=0, column=0, padx=5, pady=5)
        self.distribution_var = tk.StringVar(value="Normalny")
        self.distribution_menu = ttk.Combobox(self.generation_frame, textvariable=self.distribution_var,
                                              values=["Normalny", "Wykładniczy"])
        self.distribution_menu.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.generation_frame, text="Średnia:").grid(row=1, column=0, padx=5, pady=5)
        self.mean_entry = tk.Entry(self.generation_frame)
        self.mean_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.generation_frame, text="Odchylenie/Skala:").grid(row=2, column=0, padx=5, pady=5)
        self.std_dev_entry = tk.Entry(self.generation_frame)
        self.std_dev_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.generation_frame, text="Liczba obiektów:").grid(row=3, column=0, padx=5, pady=5)
        self.num_objects_entry = tk.Entry(self.generation_frame)
        self.num_objects_entry.grid(row=3, column=1, padx=5, pady=5)

        self.generate_button = tk.Button(self.generation_frame, text="Generuj Punkty", command=self.generate_samples)
        self.generate_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.save_button = tk.Button(root, text="Zapisz do XLSX", command=self.save_to_excel)
        self.save_button.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    def add_alternative(self):
        """Dodaje alternatywę do tabeli z automatyczną nazwą."""
        try:
            crit1 = float(self.crit1_entry.get())
            crit2 = float(self.crit2_entry.get())
            crit3 = float(self.crit3_entry.get())

            alt_number = len(self.alternatives) + 1
            name = f"Alternatywa {alt_number}"

            self.alternatives.append((alt_number, name, crit1, crit2, crit3))
            self.alt_table.insert("", "end", values=(alt_number, name, crit1, crit2, crit3))

            self.crit1_entry.delete(0, tk.END)
            self.crit2_entry.delete(0, tk.END)
            self.crit3_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawne wartości dla kryteriów.")

    def generate_samples(self):
        """Generowanie próbek danych."""
        try:
            dist = self.distribution_var.get()
            mean = float(self.mean_entry.get())
            std_dev = float(self.std_dev_entry.get())
            num_objects = int(self.num_objects_entry.get())

            if dist == "Normalny":
                self.samples = norm.rvs(loc=mean, scale=std_dev, size=(num_objects, 3))
            elif dist == "Wykładniczy":
                self.samples = expon.rvs(scale=mean, size=(num_objects, 3))
            messagebox.showinfo("Sukces", "Punkty zostały wygenerowane!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas generowania punktów: {e}")

    def save_to_excel(self):
        """Zapis alternatyw i punktów do pliku Excel."""
        if not self.alternatives and (self.samples is None or self.samples.size == 0):
            messagebox.showerror("Błąd", "Brak danych do zapisania!")
            return

        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                    if self.alternatives:
                        alt_df = pd.DataFrame(self.alternatives, columns=["Nr alternatywy", "Nazwa alternatywy", "Kryterium 1", "Kryterium 2", "Kryterium 3"])
                        alt_df.to_excel(writer, index=False, sheet_name="Arkusz1")

                    if self.samples.size > 0:
                        points_df = pd.DataFrame(self.samples, columns=["x", "y", "z"])
                        points_df.insert(0, "Nr klasy", range(1, len(points_df) + 1))
                        points_df.to_excel(writer, index=False, sheet_name="Arkusz2")

                messagebox.showinfo("Sukces", f"Dane zapisane do pliku: {file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać pliku:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = OptimizationApp(root)
    root.mainloop()