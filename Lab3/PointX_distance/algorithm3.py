import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import splprep, splev, griddata

# Definicje funkcji celu dla problemu dwukryterialnego
def F1(x, y):
    return np.sin(x) + y**2  # Nieliniowa funkcja trygonometryczno-kwadratowa

def F2(x, y):
    return np.cos(y) + x**2  # Nieliniowa funkcja trygonometryczno-kwadratowa

# Definicje funkcji celu dla problemu trzykryterialnego
def G1(x, y, z):
    return x**2 + y**2 + z**2  # Funkcja kwadratowa

def G2(x, y, z):
    return (x - 1)**2 + (y - 1)**2 + z**2  # Funkcja kwadratowa

def G3(x, y, z):
    return x * y * z  # Nieliniowa funkcja iloczynowa

# Funkcja skalaryzowana dla problemu dwukryterialnego (minimalizacja odległości)
def distance_scalarization_F(x, target_point, p=2):
    F_values = np.array([F1(x[0], x[1]), F2(x[0], x[1])])
    return np.linalg.norm(F_values - target_point, ord=p)

# Funkcja skalaryzowana dla problemu trzykryterialnego (minimalizacja odległości)
def distance_scalarization_G(x, target_point, p=2):
    G_values = np.array([G1(x[0], x[1], x[2]), G2(x[0], x[1], x[2]), G3(x[0], x[1], x[2])])
    return np.linalg.norm(G_values - target_point, ord=p)

# Generowanie zbioru Pareto dla problemu dwukryterialnego z minimalizacją odległości
def generate_pareto_set_F_distance(target_point, p=2):
    pareto_points_decision = []
    pareto_points_objective = []
    for _ in range(20):  # Liczba prób optymalizacji z różnymi punktami początkowymi
        initial_guess = np.random.uniform(-1, 1, 2)
        result = minimize(distance_scalarization_F, initial_guess, args=(target_point, p), bounds=[(-1, 1), (-1, 1)])
        if result.success:
            pareto_points_decision.append(result.x)
            pareto_points_objective.append([F1(result.x[0], result.x[1]), F2(result.x[0], result.x[1])])
    return np.array(pareto_points_decision), np.array(pareto_points_objective)

# Generowanie zbioru Pareto dla problemu trzykryterialnego z minimalizacją odległości
def generate_pareto_set_G_distance(target_point, p=2):
    pareto_points_decision = []
    pareto_points_objective = []
    for _ in range(20):  # Liczba prób optymalizacji z różnymi punktami początkowymi
        initial_guess = np.random.uniform(-1, 1, 3)
        result = minimize(distance_scalarization_G, initial_guess, args=(target_point, p), bounds=[(-1, 1), (-1, 1), (-1, 1)])
        if result.success:
            pareto_points_decision.append(result.x)
            pareto_points_objective.append([G1(result.x[0], result.x[1], result.x[2]),
                                            G2(result.x[0], result.x[1], result.x[2]),
                                            G3(result.x[0], result.x[1], result.x[2])])
    return np.array(pareto_points_decision), np.array(pareto_points_objective)

# Wizualizacja zbioru Pareto w przestrzeni decyzyjnej 2D
def plot_decision_space_2d(pareto_points, title):
    plt.figure()
    plt.plot(pareto_points[:, 0], pareto_points[:, 1], 'o', label="Punkty Pareto w przestrzeni decyzyjnej")
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()

# Wizualizacja zbioru Pareto w przestrzeni kryterialnej 2D z aproksymacją spline’ami
def plot_pareto_approximation_2d(pareto_points, title):
    pareto_points = pareto_points[np.argsort(pareto_points[:, 0])]
    try:
        tck, _ = splprep([pareto_points[:, 0], pareto_points[:, 1]], s=2)
        new_points = splev(np.linspace(0, 1, 100), tck)
        plt.figure()
        plt.plot(pareto_points[:, 0], pareto_points[:, 1], 'o', label="Dyskretne punkty Pareto")
        plt.plot(new_points[0], new_points[1], '-', label="Aproksymacja spline'ami")
    except ValueError:
        plt.figure()
        plt.plot(pareto_points[:, 0], pareto_points[:, 1], 'o-', label="Interpolacja liniowa zbioru Pareto")

    plt.xlabel("F1")
    plt.ylabel("F2")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()

# Wizualizacja zbioru Pareto w przestrzeni decyzyjnej 3D
def plot_decision_space_3d(pareto_points, title):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(pareto_points[:, 0], pareto_points[:, 1], pareto_points[:, 2], color='b')
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_zlabel("x3")
    ax.set_title(title)
    plt.show()

# Wizualizacja zbioru Pareto w przestrzeni kryterialnej 3D
def plot_pareto_approximation_3d(pareto_points, title):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(pareto_points[:, 0], pareto_points[:, 1], pareto_points[:, 2], 'o-', label="Punkty Pareto i ich aproksymacja")
    ax.set_xlabel("G1")
    ax.set_ylabel("G2")
    ax.set_zlabel("G3")
    ax.set_title(title)
    plt.legend()
    plt.show()

# Parametry: punkt dominujący i norma
target_point_2D = np.array([0, 0])  # Punkt dominujący dla 2D
target_point_3D = np.array([0, 0, 0])  # Punkt dominujący dla 3D
p_norm = 2  # Norma (np. p=2 dla normy euklidesowej)

# Obliczenia i wizualizacja dla dwukryterialnego przypadku
pareto_decision_F, pareto_objective_F = generate_pareto_set_F_distance(target_point_2D, p=p_norm)
plot_decision_space_2d(pareto_decision_F, "Zbiór P(U, F) dla problemu dwukryterialnego")
plot_pareto_approximation_2d(pareto_objective_F, "Front Pareto FP(U) dla problemu dwukryterialnego")

# Obliczenia i wizualizacja dla trzykryterialnego przypadku
pareto_decision_G, pareto_objective_G = generate_pareto_set_G_distance(target_point_3D, p=p_norm)
plot_decision_space_3d(pareto_decision_G, "Zbiór P(U, F) dla problemu trzykryterialnego")
plot_pareto_approximation_3d(pareto_objective_G, "Front Pareto FP(U) dla problemu trzykryterialnego")
