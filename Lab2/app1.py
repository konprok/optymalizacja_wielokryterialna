import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, expon
from algorithms import naive_no_filter, naive_with_filter, sort_and_filter

class OptimizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikacja Optymalizacji Wielokryterialnej")

        self.criteria = []
        
        self.plot_button = tk.Button(root, text="Generuj Wykres", command=self.plot_results)
        self.plot_button.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        self.criteria_frame = ttk.LabelFrame(root, text="Edytor Kryteriów")
        self.criteria_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.criteria_listbox = tk.Listbox(self.criteria_frame, width=30, height=10)
        self.criteria_listbox.grid(row=0, column=0, padx=5, pady=5)
        self.criteria_listbox.bind("<Double-1>", self.edit_criteria_name)

        self.add_criteria_button = tk.Button(self.criteria_frame, text="Dodaj Kryterium", command=self.add_criteria)
        self.add_criteria_button.grid(row=1, column=0, padx=5, pady=5)
        self.remove_criteria_button = tk.Button(self.criteria_frame, text="Usuń Kryterium", command=self.remove_criteria)
        self.remove_criteria_button.grid(row=2, column=0, padx=5, pady=5)

        self.generation_frame = ttk.LabelFrame(root, text="Generacja")
        self.generation_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.distribution_var = tk.StringVar(value="Normalny")
        tk.Label(self.generation_frame, text="Rozkład:").grid(row=0, column=0, padx=5, pady=5)
        self.distribution_menu = ttk.Combobox(self.generation_frame, textvariable=self.distribution_var,
                                              values=["Normalny", "Wykładniczy"])
        self.distribution_menu.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.generation_frame, text="Średnia:").grid(row=1, column=0, padx=5, pady=5)
        self.mean_entry = tk.Entry(self.generation_frame)
        self.mean_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.generation_frame, text="Odchylenie:").grid(row=2, column=0, padx=5, pady=5)
        self.std_dev_entry = tk.Entry(self.generation_frame)
        self.std_dev_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.generation_frame, text="Liczba obiektów:").grid(row=3, column=0, padx=5, pady=5)
        self.num_objects_entry = tk.Entry(self.generation_frame)
        self.num_objects_entry.grid(row=3, column=1, padx=5, pady=5)

        self.generate_button = tk.Button(self.generation_frame, text="Generuj", command=self.generate_samples)
        self.generate_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.data_frame = ttk.LabelFrame(root, text="Dane")
        self.data_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.data_table = ttk.Treeview(self.data_frame, columns=[f"Kryterium {i}" for i in range(1, 8)], show="headings")
        for i in range(1, 8):
            self.data_table.heading(f"Kryterium {i}", text=f"Kryterium {i}")
            self.data_table.column(f"Kryterium {i}", width=100)
        self.data_table.grid(row=0, column=0, padx=5, pady=5)

        self.sort_frame = ttk.LabelFrame(root, text="Akcje")
        self.sort_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.sort_criteria_var = tk.IntVar(value=1)
        tk.Label(self.sort_frame, text="Sortuj po kryterium:").grid(row=0, column=0, padx=5, pady=5)
        self.sort_criteria_entry = tk.Entry(self.sort_frame, textvariable=self.sort_criteria_var)
        self.sort_criteria_entry.grid(row=0, column=1, padx=5, pady=5)
        self.sort_button = tk.Button(self.sort_frame, text="Sortuj", command=self.sort_data)
        self.sort_button.grid(row=0, column=2, padx=5, pady=5)

        self.algorithm_var = tk.StringVar(value="Naiwny")
        tk.Label(self.sort_frame, text="Algorytm:").grid(row=1, column=0, padx=5, pady=5)
        self.algorithm_menu = ttk.Combobox(self.sort_frame, textvariable=self.algorithm_var,
                                           values=["Naiwny", "Naiwny z filtrowaniem", "Sortowanie i filtrowanie"])
        self.algorithm_menu.grid(row=1, column=1, padx=5, pady=5)
        self.benchmark_button = tk.Button(self.sort_frame, text="Benchmark", command=self.run_benchmark)
        self.benchmark_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

    def plot_results(self):
        if len(self.criteria) < 2:
            messagebox.showerror("Błąd", "Dodaj co najmniej dwa kryteria, aby wygenerować wykres.")
            return
        elif len(self.criteria) > 4:
            messagebox.showwarning("Ostrzeżenie", "Wykres można wygenerować maksymalnie dla 4 kryteriów.")
            return

        selected_algorithm = self.algorithm_var.get()
        if selected_algorithm == "Naiwny":
            result, exec_time, comparisons = naive_no_filter(self.samples)
        elif selected_algorithm == "Naiwny z filtrowaniem":
            result, exec_time, comparisons = naive_with_filter(self.samples)
        else:
            result, exec_time, comparisons = sort_and_filter(self.samples)

        non_dominated_points = np.array(result)
        all_points = np.array(self.samples)
        dominated_points = np.array([point for point in all_points if list(point) not in non_dominated_points.tolist()])

        fig = plt.figure(facecolor='white')

        algorithm_title = f"Wizualizacja wyników - Algorytm: {selected_algorithm}"

        if len(self.criteria) == 2:
            if dominated_points.ndim == 1:
                dominated_points = dominated_points.reshape(-1, 2)
            if non_dominated_points.ndim == 1:
                non_dominated_points = non_dominated_points.reshape(-1, 2)

            plt.scatter(dominated_points[:, 0], dominated_points[:, 1], c='darkred', label="Punkty zdominowane", marker='x', edgecolor='black', s=30)
            plt.scatter(non_dominated_points[:, 0], non_dominated_points[:, 1], c='darkblue', label="Punkty niezdominowane", marker='o', edgecolor='black', s=30)
            plt.xlabel(f"{self.criteria[0][0]} ({self.criteria[0][1]})")
            plt.ylabel(f"{self.criteria[1][0]} ({self.criteria[1][1]})")
            plt.legend()
            plt.title(algorithm_title)

        elif len(self.criteria) == 3:
            # Wykres 3D
            ax = fig.add_subplot(111, projection='3d')
            if dominated_points.ndim == 1:
                dominated_points = dominated_points.reshape(-1, 3)
            if non_dominated_points.ndim == 1:
                non_dominated_points = non_dominated_points.reshape(-1, 3)

            ax.scatter(dominated_points[:, 0], dominated_points[:, 1], dominated_points[:, 2], c='darkred', label="Punkty zdominowane", marker='x', edgecolor='black', s=30)
            ax.scatter(non_dominated_points[:, 0], non_dominated_points[:, 1], non_dominated_points[:, 2], c='darkblue', label="Punkty niezdominowane", marker='o', edgecolor='black', s=30)
            ax.set_xlabel(f"{self.criteria[0][0]} ({self.criteria[0][1]})")
            ax.set_ylabel(f"{self.criteria[1][0]} ({self.criteria[1][1]})")
            ax.set_zlabel(f"{self.criteria[2][0]} ({self.criteria[2][1]})")
            ax.legend()
            plt.title(algorithm_title)

        else:
            ax = fig.add_subplot(111, projection='3d')
            if dominated_points.ndim == 1:
                dominated_points = dominated_points.reshape(-1, 4)
            if non_dominated_points.ndim == 1:
                non_dominated_points = non_dominated_points.reshape(-1, 4)

            color_criteria = non_dominated_points[:, 3] if non_dominated_points.shape[1] > 3 else 'blue'
            color_criteria_d = dominated_points[:, 3] if dominated_points.shape[1] > 3 else 'red'

            sc1 = ax.scatter(non_dominated_points[:, 0], non_dominated_points[:, 1], non_dominated_points[:, 2], c=color_criteria, cmap='viridis', label="Punkty niezdominowane", marker='o', edgecolor='black', s=30)
            sc2 = ax.scatter(dominated_points[:, 0], dominated_points[:, 1], dominated_points[:, 2], c=color_criteria_d, cmap='plasma', label="Punkty zdominowane", marker='x', edgecolor='black', s=30)

            ax.set_xlabel(f"{self.criteria[0][0]} ({self.criteria[0][1]})")
            ax.set_ylabel(f"{self.criteria[1][0]} ({self.criteria[1][1]})")
            ax.set_zlabel(f"{self.criteria[2][0]} ({self.criteria[2][1]})")

            if len(self.criteria) > 3:
                cbar = plt.colorbar(sc1, label=f"{self.criteria[3][0]} ({self.criteria[3][1]})", pad=0.15)

            plt.title(algorithm_title)

        plt.show()



    def add_criteria(self):
        criteria_name = f"Kryterium {len(self.criteria) + 1}"
        direction = "Min" if len(self.criteria) % 2 == 0 else "Max"
        direction = simpledialog.askstring("Kierunek", "Podaj kierunek dla nowego kryterium (Min/Max):", initialvalue=direction)
        if direction not in ["Min", "Max"]:
            messagebox.showerror("Błąd", "Kierunek musi być Min lub Max")
            return
        self.criteria.append((criteria_name, direction))
        self.criteria_listbox.insert(tk.END, f"{criteria_name} - {direction}")

    def edit_criteria_name(self, event):
        selection = self.criteria_listbox.curselection()
        if selection:
            index = selection[0]
            new_name = simpledialog.askstring("Edycja Nazwy", "Podaj nową nazwę kryterium:", initialvalue=self.criteria[index][0])
            direction = simpledialog.askstring("Kierunek", "Podaj kierunek dla kryterium (Min/Max):", initialvalue=self.criteria[index][1])
            if direction not in ["Min", "Max"]:
                messagebox.showerror("Błąd", "Kierunek musi być Min lub Max")
                return
            if new_name:
                self.criteria[index] = (new_name, direction)
                self.criteria_listbox.delete(index)
                self.criteria_listbox.insert(index, f"{new_name} - {direction}")

    def remove_criteria(self):
        selection = self.criteria_listbox.curselection()
        if selection:
            index = selection[0]
            del self.criteria[index]
            self.criteria_listbox.delete(index)

    def generate_samples(self):
        dist = self.distribution_var.get()
        mean = float(self.mean_entry.get())
        std_dev = float(self.std_dev_entry.get())
        num_objects = int(self.num_objects_entry.get())

        if dist == "Normalny":
            self.samples = norm.rvs(loc=mean, scale=std_dev, size=(num_objects, len(self.criteria)))
        elif dist == "Wykładniczy":
            self.samples = expon.rvs(scale=mean, size=(num_objects, len(self.criteria)))

        for row in self.data_table.get_children():
            self.data_table.delete(row)
        for sample in self.samples:
            self.data_table.insert("", "end", values=list(map(lambda x: round(x, 2), sample)))

    def sort_data(self):
        criterion_index = self.sort_criteria_var.get() - 1
        self.samples = self.samples[self.samples[:, criterion_index].argsort()]
        
        for row in self.data_table.get_children():
            self.data_table.delete(row)
        for sample in self.samples:
            self.data_table.insert("", "end", values=list(map(lambda x: round(x, 2), sample)))

    def run_benchmark(self):
        alg = self.algorithm_var.get()
        if alg == "Naiwny":
            result, exec_time, comparisons = naive_no_filter(self.samples)
        elif alg == "Naiwny z filtrowaniem":
            result, exec_time, comparisons = naive_with_filter(self.samples)
        else:
            result, exec_time, comparisons = sort_and_filter(self.samples)

        messagebox.showinfo("Benchmark", f"Wyniki dla algorytmu {alg}:\nCzas: {exec_time}\nPorównania: {comparisons}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OptimizationApp(root)
    root.mainloop()