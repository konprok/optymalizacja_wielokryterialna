import tkinter as tk
from tkinter import ttk, messagebox

def load_laptops_mock():
    return {
        "1": {
            "brand": "DELL",
            "model": "7400",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 3.9,
            "res_width": 1980,
            "res_height": 1080,
            "ssd_gb": 256,
            "ram_gb": 16,
            "battery_hours": 13,
            "price": 8299,
            "warranty_months": 36,
            "gpu_type": "zintegrowana",
            "gpu_score": 1,
            "screen_size_inch": 14
        },
        "2": {
            "brand": "MS",
            "model": "surface book",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 4.2,
            "res_width": 3000,
            "res_height": 2000,
            "ssd_gb": 256,
            "ram_gb": 8,
            "battery_hours": 17,
            "price": 7399,
            "warranty_months": 12,
            "gpu_type": "GTX 1050",
            "gpu_score": 4,
            "screen_size_inch": 13
        },
        "3": {
            "brand": "Acer",
            "model": "swift 3",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 3.5,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 128,
            "ram_gb": 4,
            "battery_hours": 3,
            "price": 3200,
            "warranty_months": 24,
            "gpu_type": "zintegrowana",
            "gpu_score": 1,
            "screen_size_inch": 14
        },
        "4": {
            "brand": "MSI",
            "model": "gl75",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 4.5,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 256,
            "ram_gb": 8,
            "battery_hours": 4,
            "price": 4549,
            "warranty_months": 24,
            "gpu_type": "gtx 1660Ti",
            "gpu_score": 7,
            "screen_size_inch": 17
        },
        "5": {
            "brand": "Lenovo",
            "model": "thinkpad t470",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 3.7,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 256,
            "ram_gb": 12,
            "battery_hours": 7,
            "price": 3899,
            "warranty_months": 24,
            "gpu_type": "zintegrowana",
            "gpu_score": 2,
            "screen_size_inch": 14
        },
        "6": {
            "brand": "MS",
            "model": "surface book",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 3.7,
            "res_width": 3000,
            "res_height": 2000,
            "ssd_gb": 256,
            "ram_gb": 8,
            "battery_hours": 12,
            "price": 8199,
            "warranty_months": 12,
            "gpu_type": "zintegrowana",
            "gpu_score": 2,
            "screen_size_inch": 13
        },
        "7": {
            "brand": "Huawei",
            "model": "matebook d14",
            "cpu_producer": "amd",
            "cpu_cores": 4,
            "cpu_freq": 3.5,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 256,
            "ram_gb": 8,
            "battery_hours": 6,
            "price": 2999,
            "warranty_months": 24,
            "gpu_type": "zintegrowana",
            "gpu_score": 2,
            "screen_size_inch": 14
        },
        "8": {
            "brand": "Apple",
            "model": "Macbook Air 2017",
            "cpu_producer": "intel",
            "cpu_cores": 2,
            "cpu_freq": 3.5,
            "res_width": 2560,
            "res_height": 1600,
            "ssd_gb": 256,
            "ram_gb": 8,
            "battery_hours": 12,
            "price": 4499,
            "warranty_months": 12,
            "gpu_type": "zintegrowana",
            "gpu_score": 2,
            "screen_size_inch": 13
        },
        "9": {
            "brand": "Lenovo",
            "model": "Legion Y740",
            "cpu_producer": "intel",
            "cpu_cores": 6,
            "cpu_freq": 4.5,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 512,
            "ram_gb": 16,
            "battery_hours": 3,
            "price": 9999,
            "warranty_months": 24,
            "gpu_type": "NVIDIA GeForce",
            "gpu_score": 7,
            "screen_size_inch": 15.6
        },
        "10": {
            "brand": "Asus",
            "model": "ZenBook ux3",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 4.7,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 512,
            "ram_gb": 16,
            "battery_hours": 10,
            "price": 5099,
            "warranty_months": 24,
            "gpu_type": "NVIDIA GeForce",
            "gpu_score": 6,
            "screen_size_inch": 14
        },
        "11": {
            "brand": "HP",
            "model": "EliteBook 840",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 3.5,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 960,
            "ram_gb": 32,
            "battery_hours": 10,
            "price": 7699,
            "warranty_months": 36,
            "gpu_type": "zintegrowana",
            "gpu_score": 2,
            "screen_size_inch": 14
        },
        "12": {
            "brand": "MSI",
            "model": "Prestige 14",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 4.7,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 512,
            "ram_gb": 16,
            "battery_hours": 10,
            "price": 5099,
            "warranty_months": 24,
            "gpu_type": "NVIDIA GeForce",
            "gpu_score": 5,
            "screen_size_inch": 14
        },
        "13": {
            "brand": "Lenovo",
            "model": "thinkpad t495",
            "cpu_producer": "amd",
            "cpu_cores": 4,
            "cpu_freq": 3.5,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 128,
            "ram_gb": 8,
            "battery_hours": 15,
            "price": 5699,
            "warranty_months": 24,
            "gpu_type": "AMD Radeon",
            "gpu_score": 3,
            "screen_size_inch": 14
        },
        "14": {
            "brand": "Lenovo",
            "model": "prection 355",
            "cpu_producer": "intel",
            "cpu_cores": 6,
            "cpu_freq": 4.5,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 512,
            "ram_gb": 32,
            "battery_hours": 20,
            "price": 10499,
            "warranty_months": 36,
            "gpu_type": "NVIDIA Quadro",
            "gpu_score": 7,
            "screen_size_inch": 15
        },
        "15": {
            "brand": "DELL",
            "model": "vostro 5501",
            "cpu_producer": "intel",
            "cpu_cores": 4,
            "cpu_freq": 3.7,
            "res_width": 1920,
            "res_height": 1080,
            "ssd_gb": 512,
            "ram_gb": 16,
            "battery_hours": 4,
            "price": 4399,
            "warranty_months": 24,
            "gpu_type": "zintegrowana",
            "gpu_score": 1,
            "screen_size_inch": 15
        }
    }

def laptop_passes_filter(lap_info, preferences):
    """
    Sprawdza warunki:
      - cena <= max_price
      - RAM >= min_ram
      - SSD >= min_ssd
    """
    max_price = preferences.get("max_price", None)
    if max_price is not None and lap_info.get("price", 9999999) > max_price:
        return False

    min_ram = preferences.get("min_ram", None)
    if min_ram is not None and lap_info.get("ram_gb", 0) < min_ram:
        return False

    min_ssd = preferences.get("min_ssd", None)
    if min_ssd is not None and lap_info.get("ssd_gb", 0) < min_ssd:
        return False

    return True

def compute_score_saw(laptop_info, preferences):
    """
    Proste SAW z 4 kryteriami:
      - cpu_freq  (benefit)
      - price     (cost -> ujemna waga)
      - battery_hours (benefit)
      - ram_gb    (benefit)
    """
    w_cpu   = preferences.get("weight_cpu", 0.0)
    w_price = preferences.get("weight_price", 0.0)   # cost
    w_batt  = preferences.get("weight_battery", 0.0)
    w_ram   = preferences.get("weight_ram", 0.0)

    cpu  = laptop_info.get("cpu_freq", 0.0)
    pric = laptop_info.get("price", 999999)
    batt = laptop_info.get("battery_hours", 0.0)
    ram  = laptop_info.get("ram_gb", 0.0)

    score = (w_cpu * cpu) + (w_price * pric) + (w_batt * batt) + (w_ram * ram)
    return score

def recommend_best_laptop_saw(laptops_data, preferences, excluded_ids=None):
    """
    - Wyklucza laptopy z 'excluded_ids'
    - Sprawdza filtr
    - Liczy score
    - Zwraca 1 najlepszy laptop (lub None, gdy brak)
    """
    if excluded_ids is None:
        excluded_ids = set()

    best_laptop = None
    best_score  = -999999999

    for lap_id, lap_info in laptops_data.items():
        if lap_id in excluded_ids:
            continue
        if not laptop_passes_filter(lap_info, preferences):
            continue

        sc = compute_score_saw(lap_info, preferences)
        if sc > best_score:
            best_score = sc
            best_laptop = (lap_id, lap_info)

    return best_laptop

class LaptopRecommenderApp(tk.Tk):
    def __init__(self, laptops_data):
        super().__init__()
        self.title("Laptop Recommender - SAW")
        self.geometry("950x600")

        self.laptops_data = laptops_data
        self.excluded_ids = set()

        self.build_gui()

    def build_gui(self):
        left_frame = tk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        tk.Label(left_frame, text="Wszystkie laptopy:").pack(anchor=tk.W)
        self.laptops_list = tk.Listbox(left_frame, height=20, width=40)
        self.laptops_list.pack(fill=tk.BOTH, expand=True)

        self.populate_laptops_list()

        tk.Button(left_frame, text="Dodaj do niechcianych ->",
                  command=self.add_to_excluded).pack(pady=5)

        tk.Label(left_frame, text="Nie chcę kupować:").pack(anchor=tk.W)
        self.excluded_list = tk.Listbox(left_frame, height=8, width=40)
        self.excluded_list.pack(fill=tk.BOTH, expand=True)

        tk.Button(left_frame, text="Usuń z niechcianych",
                  command=self.remove_from_excluded).pack(pady=5)

        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        filters_frame = tk.LabelFrame(right_frame, text="Filtry")
        filters_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(filters_frame, text="Maks. cena:").grid(row=0, column=0, sticky=tk.W)
        self.max_price_var = tk.IntVar(value=999999)
        tk.Entry(filters_frame, textvariable=self.max_price_var, width=10).grid(row=0, column=1, sticky=tk.W)

        tk.Label(filters_frame, text="Min. RAM:").grid(row=1, column=0, sticky=tk.W)
        self.min_ram_var = tk.IntVar(value=0)
        tk.Entry(filters_frame, textvariable=self.min_ram_var, width=10).grid(row=1, column=1, sticky=tk.W)

        tk.Label(filters_frame, text="Min. SSD (GB):").grid(row=2, column=0, sticky=tk.W)
        self.min_ssd_var = tk.IntVar(value=0)
        tk.Entry(filters_frame, textvariable=self.min_ssd_var, width=10).grid(row=2, column=1, sticky=tk.W)

        weights_frame = tk.LabelFrame(right_frame, text="Wagi (SAW)")
        weights_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(weights_frame, text="CPU freq (benefit):").grid(row=0, column=0, sticky=tk.W)
        self.scale_cpu = tk.Scale(weights_frame, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL)
        self.scale_cpu.set(0.5)
        self.scale_cpu.grid(row=0, column=1, sticky=tk.W)

        tk.Label(weights_frame, text="Cena (cost, ujemna):").grid(row=1, column=0, sticky=tk.W)
        self.scale_price = tk.Scale(weights_frame, from_=-1, to=0, resolution=0.1, orient=tk.HORIZONTAL)
        self.scale_price.set(-0.3)
        self.scale_price.grid(row=1, column=1, sticky=tk.W)

        tk.Label(weights_frame, text="Bateria (benefit):").grid(row=2, column=0, sticky=tk.W)
        self.scale_battery = tk.Scale(weights_frame, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL)
        self.scale_battery.set(0.2)
        self.scale_battery.grid(row=2, column=1, sticky=tk.W)

        tk.Label(weights_frame, text="RAM (benefit):").grid(row=3, column=0, sticky=tk.W)
        self.scale_ram = tk.Scale(weights_frame, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL)
        self.scale_ram.set(0.2)
        self.scale_ram.grid(row=3, column=1, sticky=tk.W)

        tk.Button(right_frame, text="Rekomenduj (SAW)", command=self.do_recommendation).pack(pady=10)

        tk.Label(right_frame, text="Najlepszy laptop:").pack(anchor=tk.W)
        self.result_text = tk.Text(right_frame, height=14, width=50)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def populate_laptops_list(self):
        """Wypełnienie listy laptopów."""
        self.laptops_list.delete(0, tk.END)
        for lap_id, info in self.laptops_data.items():
            display = f"{lap_id} - {info['brand']} {info['model']} (Price={info['price']})"
            self.laptops_list.insert(tk.END, display)

    def add_to_excluded(self):
        """Przeniesienie zaznaczonego laptopa do listy niechcianych."""
        sel = self.laptops_list.curselection()
        if not sel:
            messagebox.showwarning("Brak wyboru", "Najpierw wybierz laptop z listy po lewej.")
            return
        index = sel[0]
        text_line = self.laptops_list.get(index)
        lap_id = text_line.split(" - ")[0].strip()

        if lap_id not in self.excluded_ids:
            self.excluded_ids.add(lap_id)
            self.excluded_list.insert(tk.END, text_line)

    def remove_from_excluded(self):
        """Usunięcie laptopa z listy niechcianych."""
        sel = self.excluded_list.curselection()
        if not sel:
            return
        index = sel[0]
        text_line = self.excluded_list.get(index)
        lap_id = text_line.split(" - ")[0].strip()

        self.excluded_ids.discard(lap_id)
        self.excluded_list.delete(index)

    def do_recommendation(self):
        """Oblicza 1 najlepszy laptop SAW, pomijając excluded_ids."""
        prefs = {
            "max_price": self.max_price_var.get(),
            "min_ram": self.min_ram_var.get(),
            "min_ssd": self.min_ssd_var.get(),
            "weight_cpu":    self.scale_cpu.get(),
            "weight_price":  self.scale_price.get(),
            "weight_battery":self.scale_battery.get(),
            "weight_ram":    self.scale_ram.get()
        }

        best = recommend_best_laptop_saw(self.laptops_data, prefs, excluded_ids=self.excluded_ids)
        self.result_text.delete("1.0", tk.END)

        if best is None:
            self.result_text.insert(tk.END, "Brak laptopa spełniającego kryteria.")
        else:
            lap_id, lap_info = best
            self.result_text.insert(
                tk.END,
                f"ID: {lap_id}\n"
                f"Marka: {lap_info['brand']}\n"
                f"Model: {lap_info['model']}\n"
                f"Producent CPU: {lap_info['cpu_producer']}\n"
                f"Liczba rdzeni CPU: {lap_info['cpu_cores']}\n"
                f"Częstotliwość CPU: {lap_info['cpu_freq']} GHz\n"
                f"Rozdzielczość: {lap_info['res_width']} x {lap_info['res_height']}\n"
                f"SSD: {lap_info['ssd_gb']} GB\n"
                f"RAM: {lap_info['ram_gb']} GB\n"
                f"Czas pracy na baterii: {lap_info['battery_hours']} h\n"
                f"Cena: {lap_info['price']} PLN\n"
                f"Gwarancja: {lap_info['warranty_months']} mies.\n"
                f"GPU: {lap_info['gpu_type']} (ocena: {lap_info['gpu_score']})\n"
                f"Przekątna ekranu: {lap_info['screen_size_inch']} cali\n"
            )

def main():
    laptops_data = load_laptops_mock()
    app = LaptopRecommenderApp(laptops_data)
    app.mainloop()

if __name__ == "__main__":
    main()